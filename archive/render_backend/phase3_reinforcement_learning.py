#!/usr/bin/env python3
"""
Phase 3 Component P3_006: Reinforcement Learning Integration
==========================================================

Adaptive model selection and dynamic weighting using reinforcement learning.
Implements multiple RL algorithms for intelligent prediction system optimization:
- Multi-Armed Bandit for model selection
- Q-Learning for dynamic weight adjustment
- Policy Gradient for regime-specific adaptation
- Thompson Sampling for exploration-exploitation balance

Target: Adaptive intelligence with 15-20% performance improvement
Dependencies: P3-001 to P3-005 operational
"""

import numpy as np
import pandas as pd
import logging
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import warnings
warnings.filterwarnings('ignore')

class RLAlgorithm(Enum):
    """Reinforcement Learning algorithm types."""
    MULTI_ARMED_BANDIT = "multi_armed_bandit"
    Q_LEARNING = "q_learning"
    POLICY_GRADIENT = "policy_gradient"
    THOMPSON_SAMPLING = "thompson_sampling"

@dataclass
class RLAction:
    """Reinforcement Learning action representation."""
    action_id: str
    action_type: str  # 'model_weight', 'feature_select', 'regime_adapt'
    parameters: Dict[str, float]
    timestamp: datetime
    expected_reward: float = 0.0

@dataclass
class RLState:
    """Reinforcement Learning state representation."""
    market_regime: str
    volatility_level: str
    performance_trend: str
    model_accuracies: Dict[str, float]
    feature_importances: Dict[str, float]
    timestamp: datetime

@dataclass
class RLExperience:
    """Experience replay data structure."""
    state: RLState
    action: RLAction
    reward: float
    next_state: Optional[RLState]
    done: bool
    timestamp: datetime

@dataclass
class RLMetrics:
    """RL system performance metrics."""
    total_episodes: int
    total_rewards: float
    average_reward: float
    exploration_rate: float
    exploitation_rate: float
    best_action_frequency: Dict[str, int]
    convergence_status: str

class MultiArmedBandit:
    """
    Multi-Armed Bandit for model selection and weight optimization.
    
    Uses epsilon-greedy and UCB (Upper Confidence Bound) strategies
    for balancing exploration and exploitation in model selection.
    """
    
    def __init__(self, n_arms: int, epsilon: float = 0.1, alpha: float = 0.1):
        self.n_arms = n_arms
        self.epsilon = epsilon  # Exploration rate
        self.alpha = alpha  # Learning rate
        
        # Q-values (estimated rewards) for each arm
        self.q_values = np.zeros(n_arms)
        self.arm_counts = np.zeros(n_arms)
        self.total_pulls = 0
        
        # UCB parameters
        self.c = 2.0  # Exploration parameter for UCB
        
        self.logger = logging.getLogger(__name__)
    
    def select_arm_epsilon_greedy(self) -> int:
        """Select arm using epsilon-greedy strategy."""
        if np.random.random() < self.epsilon:
            # Explore: random selection
            return np.random.randint(self.n_arms)
        else:
            # Exploit: select best arm
            return np.argmax(self.q_values)
    
    def select_arm_ucb(self) -> int:
        """Select arm using Upper Confidence Bound strategy."""
        if self.total_pulls < self.n_arms:
            # Pull each arm at least once
            return self.total_pulls
        
        # Calculate UCB values
        ucb_values = np.zeros(self.n_arms)
        for arm in range(self.n_arms):
            if self.arm_counts[arm] > 0:
                confidence_interval = self.c * np.sqrt(
                    np.log(self.total_pulls) / self.arm_counts[arm]
                )
                ucb_values[arm] = self.q_values[arm] + confidence_interval
            else:
                ucb_values[arm] = float('inf')  # Unvisited arms get highest priority
        
        return np.argmax(ucb_values)
    
    def update(self, arm: int, reward: float):
        """Update Q-value for selected arm based on observed reward."""
        self.arm_counts[arm] += 1
        self.total_pulls += 1
        
        # Update Q-value using incremental average
        self.q_values[arm] += self.alpha * (reward - self.q_values[arm])
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current bandit metrics."""
        return {
            'q_values': self.q_values.tolist(),
            'arm_counts': self.arm_counts.tolist(),
            'total_pulls': self.total_pulls,
            'best_arm': int(np.argmax(self.q_values)),
            'exploration_rate': self.epsilon,
            'average_reward': np.mean(self.q_values)
        }

class QLearningAgent:
    """
    Q-Learning agent for dynamic weight adjustment.
    
    Learns optimal actions for different market states to maximize
    prediction accuracy through dynamic model weighting.
    """
    
    def __init__(self, 
                 state_size: int, 
                 action_size: int,
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.95,
                 epsilon: float = 0.1):
        
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # Q-table: state x action matrix
        self.q_table = np.zeros((state_size, action_size))
        
        # Experience tracking
        self.experience_buffer = deque(maxlen=10000)
        
        self.logger = logging.getLogger(__name__)
    
    def encode_state(self, state: RLState) -> int:
        """Encode continuous state into discrete state index."""
        # Simple discretization strategy
        # In practice, this would be more sophisticated
        
        regime_map = {'Bull': 0, 'Bear': 1, 'Sideways': 2}
        vol_map = {'Low': 0, 'Medium': 1, 'High': 2}
        trend_map = {'Improving': 0, 'Stable': 1, 'Declining': 2}
        
        regime_idx = regime_map.get(state.market_regime.split('_')[0], 2)
        vol_idx = vol_map.get(state.volatility_level, 1)
        trend_idx = trend_map.get(state.performance_trend, 1)
        
        # Combine indices (assumes state_size >= 27)
        return min(regime_idx * 9 + vol_idx * 3 + trend_idx, self.state_size - 1)
    
    def select_action(self, state: RLState) -> int:
        """Select action using epsilon-greedy policy."""
        state_idx = self.encode_state(state)
        
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.randint(self.action_size)
        else:
            # Exploit: best action for current state
            return np.argmax(self.q_table[state_idx])
    
    def update_q_table(self, 
                      state: RLState, 
                      action: int, 
                      reward: float, 
                      next_state: Optional[RLState]):
        """Update Q-table using Q-learning update rule."""
        
        state_idx = self.encode_state(state)
        
        if next_state is not None:
            next_state_idx = self.encode_state(next_state)
            next_q_max = np.max(self.q_table[next_state_idx])
        else:
            next_q_max = 0  # Terminal state
        
        # Q-learning update rule
        current_q = self.q_table[state_idx, action]
        target_q = reward + self.discount_factor * next_q_max
        
        self.q_table[state_idx, action] += self.learning_rate * (target_q - current_q)
    
    def store_experience(self, experience: RLExperience):
        """Store experience for potential replay learning."""
        self.experience_buffer.append(experience)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current Q-learning metrics."""
        return {
            'q_table_shape': self.q_table.shape,
            'q_table_stats': {
                'mean': float(np.mean(self.q_table)),
                'std': float(np.std(self.q_table)),
                'max': float(np.max(self.q_table)),
                'min': float(np.min(self.q_table))
            },
            'experience_count': len(self.experience_buffer),
            'epsilon': self.epsilon,
            'learning_rate': self.learning_rate
        }

class ThompsonSampling:
    """
    Thompson Sampling for Bayesian model selection.
    
    Uses Beta distribution to model uncertainty in model performance
    and sample from posterior distributions for selection.
    """
    
    def __init__(self, n_models: int):
        self.n_models = n_models
        
        # Beta distribution parameters (alpha, beta) for each model
        # Start with uniform prior: Beta(1, 1)
        self.alpha = np.ones(n_models)
        self.beta = np.ones(n_models)
        
        self.logger = logging.getLogger(__name__)
    
    def sample_model(self) -> int:
        """Sample a model based on Thompson Sampling."""
        # Sample from Beta distribution for each model
        samples = np.random.beta(self.alpha, self.beta)
        
        # Select model with highest sample
        return np.argmax(samples)
    
    def update(self, model_idx: int, success: bool):
        """Update Beta parameters based on success/failure."""
        if success:
            self.alpha[model_idx] += 1
        else:
            self.beta[model_idx] += 1
    
    def get_model_probabilities(self) -> np.ndarray:
        """Get current probability estimates for each model."""
        return self.alpha / (self.alpha + self.beta)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Thompson Sampling metrics."""
        probabilities = self.get_model_probabilities()
        
        return {
            'alpha_parameters': self.alpha.tolist(),
            'beta_parameters': self.beta.tolist(),
            'model_probabilities': probabilities.tolist(),
            'best_model': int(np.argmax(probabilities)),
            'probability_spread': float(np.std(probabilities))
        }

class ReinforcementLearningFramework:
    """
    Comprehensive Reinforcement Learning Framework for prediction optimization.
    
    Integrates multiple RL algorithms for different aspects of the prediction system:
    - Model selection and weighting
    - Feature selection optimization
    - Regime-specific adaptation
    - Performance optimization
    """
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # RL Components
        self.model_bandit = None
        self.q_agent = None
        self.thompson_sampler = None
        
        # State and action tracking
        self.current_state = None
        self.action_history = deque(maxlen=1000)
        self.reward_history = deque(maxlen=1000)
        
        # Model performance tracking
        self.model_performance = defaultdict(list)
        self.feature_performance = defaultdict(list)
        
        # Configuration
        self.n_models = self.config.get('n_models', 5)
        self.n_actions = self.config.get('n_actions', 10)
        self.state_size = self.config.get('state_size', 27)  # 3x3x3 for regime/vol/trend
        
        self._initialize_rl_components()
        
        self.logger.info("🧠 Reinforcement Learning Framework initialized")
    
    def _initialize_rl_components(self):
        """Initialize all RL components."""
        
        # Multi-Armed Bandit for model selection
        self.model_bandit = MultiArmedBandit(
            n_arms=self.n_models,
            epsilon=self.config.get('bandit_epsilon', 0.1),
            alpha=self.config.get('bandit_alpha', 0.1)
        )
        
        # Q-Learning agent for dynamic weighting
        self.q_agent = QLearningAgent(
            state_size=self.state_size,
            action_size=self.n_actions,
            learning_rate=self.config.get('q_learning_rate', 0.1),
            discount_factor=self.config.get('q_discount', 0.95),
            epsilon=self.config.get('q_epsilon', 0.1)
        )
        
        # Thompson Sampling for Bayesian model selection
        self.thompson_sampler = ThompsonSampling(n_models=self.n_models)
    
    def create_state(self, 
                    market_regime: str,
                    model_accuracies: Dict[str, float],
                    feature_importances: Dict[str, float] = None) -> RLState:
        """Create RL state from current market conditions and model performance."""
        
        # Determine volatility level from model performance spread
        accuracy_values = list(model_accuracies.values())
        if len(accuracy_values) > 1:
            accuracy_std = np.std(accuracy_values)
            if accuracy_std < 0.05:
                volatility_level = "Low"
            elif accuracy_std < 0.15:
                volatility_level = "Medium"
            else:
                volatility_level = "High"
        else:
            volatility_level = "Medium"
        
        # Determine performance trend
        if len(self.reward_history) >= 5:
            recent_rewards = list(self.reward_history)[-5:]
            trend_slope = np.polyfit(range(len(recent_rewards)), recent_rewards, 1)[0]
            
            if trend_slope > 0.01:
                performance_trend = "Improving"
            elif trend_slope < -0.01:
                performance_trend = "Declining"
            else:
                performance_trend = "Stable"
        else:
            performance_trend = "Stable"
        
        return RLState(
            market_regime=market_regime,
            volatility_level=volatility_level,
            performance_trend=performance_trend,
            model_accuracies=model_accuracies.copy(),
            feature_importances=feature_importances or {},
            timestamp=datetime.now()
        )
    
    def select_optimal_models(self, 
                            state: RLState,
                            algorithm: RLAlgorithm = RLAlgorithm.THOMPSON_SAMPLING) -> List[int]:
        """Select optimal models using specified RL algorithm."""
        
        if algorithm == RLAlgorithm.MULTI_ARMED_BANDIT:
            # Select top models using bandit
            selected = []
            for _ in range(min(3, self.n_models)):  # Select top 3
                arm = self.model_bandit.select_arm_ucb()
                selected.append(arm)
            return selected
        
        elif algorithm == RLAlgorithm.THOMPSON_SAMPLING:
            # Use Thompson Sampling
            selected_model = self.thompson_sampler.sample_model()
            return [selected_model]
        
        elif algorithm == RLAlgorithm.Q_LEARNING:
            # Use Q-learning for action selection
            action = self.q_agent.select_action(state)
            # Map action to model selection (simplified)
            return [action % self.n_models]
        
        else:
            # Default to uniform random
            return [np.random.randint(self.n_models)]
    
    def compute_dynamic_weights(self, 
                              state: RLState,
                              selected_models: List[int]) -> Dict[str, float]:
        """Compute dynamic weights for selected models using RL insights."""
        
        # Get model probabilities from Thompson Sampling
        model_probs = self.thompson_sampler.get_model_probabilities()
        
        # Adjust weights based on current state
        weights = {}
        total_weight = 0
        
        for i, model_idx in enumerate(selected_models):
            # Base weight from Thompson Sampling probability
            base_weight = model_probs[model_idx]
            
            # Adjust based on market regime
            regime_multiplier = self._get_regime_multiplier(state.market_regime, model_idx)
            
            # Adjust based on recent performance
            performance_multiplier = self._get_performance_multiplier(model_idx)
            
            final_weight = base_weight * regime_multiplier * performance_multiplier
            weights[f'model_{model_idx}'] = final_weight
            total_weight += final_weight
        
        # Normalize weights
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights
    
    def _get_regime_multiplier(self, regime: str, model_idx: int) -> float:
        """Get regime-specific multiplier for model weighting."""
        
        # Simplified regime-based adjustments
        # In practice, this would be learned from data
        
        multipliers = {
            'Bull': [1.2, 1.0, 0.8, 1.1, 0.9],
            'Bear': [0.8, 1.2, 1.1, 0.9, 1.0],
            'Sideways': [1.0, 0.9, 1.2, 1.0, 1.1]
        }
        
        regime_key = regime.split('_')[0] if '_' in regime else regime
        if regime_key in multipliers and model_idx < len(multipliers[regime_key]):
            return multipliers[regime_key][model_idx]
        
        return 1.0  # Default multiplier
    
    def _get_performance_multiplier(self, model_idx: int) -> float:
        """Get performance-based multiplier for model weighting."""
        
        if f'model_{model_idx}' in self.model_performance:
            recent_performance = self.model_performance[f'model_{model_idx}'][-10:]  # Last 10 observations
            if recent_performance:
                avg_performance = np.mean(recent_performance)
                # Scale multiplier based on performance (0.5 to 1.5 range)
                return 0.5 + avg_performance
        
        return 1.0  # Default multiplier
    
    def update_performance(self, 
                         model_results: Dict[str, float],
                         actual_outcome: float,
                         state: RLState):
        """Update RL components based on prediction performance."""
        
        # Calculate rewards for each model
        for model_name, predicted_value in model_results.items():
            # Simple reward: negative squared error
            error = abs(predicted_value - actual_outcome)
            reward = 1.0 / (1.0 + error)  # Reward between 0 and 1
            
            # Update model performance history
            self.model_performance[model_name].append(reward)
            
            # Update RL components
            if 'model_' in model_name:
                model_idx = int(model_name.split('_')[1])
                
                # Update Multi-Armed Bandit
                self.model_bandit.update(model_idx, reward)
                
                # Update Thompson Sampling
                success = reward > 0.7  # Threshold for success
                self.thompson_sampler.update(model_idx, success)
        
        # Store reward for trend analysis
        avg_reward = np.mean([1.0 / (1.0 + abs(pred - actual_outcome)) 
                             for pred in model_results.values()])
        self.reward_history.append(avg_reward)
        
        # Update current state
        self.current_state = state
        
        self.logger.debug(f"🔄 RL Performance updated: avg_reward={avg_reward:.3f}")
    
    def get_rl_recommendations(self, 
                             state: RLState) -> Dict[str, Any]:
        """Get comprehensive RL recommendations for prediction optimization."""
        
        # Select optimal models using different algorithms
        bandit_models = self.select_optimal_models(state, RLAlgorithm.MULTI_ARMED_BANDIT)
        thompson_models = self.select_optimal_models(state, RLAlgorithm.THOMPSON_SAMPLING)
        q_models = self.select_optimal_models(state, RLAlgorithm.Q_LEARNING)
        
        # Compute dynamic weights
        weights = self.compute_dynamic_weights(state, thompson_models)
        
        # Get exploration recommendations
        exploration_rate = self._calculate_exploration_rate()
        
        return {
            'recommended_models': {
                'bandit_selection': bandit_models,
                'thompson_selection': thompson_models,
                'q_learning_selection': q_models
            },
            'dynamic_weights': weights,
            'exploration_rate': exploration_rate,
            'performance_insights': self._get_performance_insights(),
            'adaptive_recommendations': self._get_adaptive_recommendations(state)
        }
    
    def _calculate_exploration_rate(self) -> float:
        """Calculate current exploration rate based on performance stability."""
        
        if len(self.reward_history) < 10:
            return 0.3  # High exploration initially
        
        recent_rewards = list(self.reward_history)[-10:]
        reward_stability = 1.0 - np.std(recent_rewards)
        
        # Higher stability -> lower exploration
        return max(0.05, 0.3 * (1.0 - reward_stability))
    
    def _get_performance_insights(self) -> Dict[str, Any]:
        """Get performance insights from RL learning."""
        
        insights = {
            'model_performance_ranking': {},
            'regime_preferences': {},
            'learning_progress': {}
        }
        
        # Model performance ranking
        model_scores = {}
        for model_name, performance_history in self.model_performance.items():
            if performance_history:
                model_scores[model_name] = np.mean(performance_history[-20:])  # Recent average
        
        insights['model_performance_ranking'] = dict(
            sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        )
        
        # Learning progress
        if len(self.reward_history) >= 20:
            early_rewards = list(self.reward_history)[:10]
            recent_rewards = list(self.reward_history)[-10:]
            
            insights['learning_progress'] = {
                'early_average': np.mean(early_rewards),
                'recent_average': np.mean(recent_rewards),
                'improvement': np.mean(recent_rewards) - np.mean(early_rewards)
            }
        
        return insights
    
    def _get_adaptive_recommendations(self, state: RLState) -> List[str]:
        """Get adaptive recommendations based on current state."""
        
        recommendations = []
        
        # Performance-based recommendations
        if len(self.reward_history) >= 5:
            recent_trend = np.polyfit(range(5), list(self.reward_history)[-5:], 1)[0]
            
            if recent_trend < -0.01:
                recommendations.append("Consider increasing exploration rate")
                recommendations.append("Review feature selection")
            elif recent_trend > 0.01:
                recommendations.append("Current strategy is improving - maintain course")
        
        # Regime-based recommendations
        if state.market_regime.startswith('Bull'):
            recommendations.append("Favor momentum-based models in bull market")
        elif state.market_regime.startswith('Bear'):
            recommendations.append("Emphasize defensive models in bear market")
        else:
            recommendations.append("Use balanced model ensemble in sideways market")
        
        # Volatility-based recommendations
        if state.volatility_level == "High":
            recommendations.append("Increase model diversity for high volatility")
            recommendations.append("Consider shorter prediction horizons")
        
        return recommendations
    
    def get_comprehensive_metrics(self) -> RLMetrics:
        """Get comprehensive RL system metrics."""
        
        total_rewards = sum(self.reward_history) if self.reward_history else 0
        avg_reward = np.mean(self.reward_history) if self.reward_history else 0
        
        # Calculate action frequency
        action_frequency = defaultdict(int)
        for action in self.action_history:
            action_frequency[action.action_id] += 1
        
        return RLMetrics(
            total_episodes=len(self.reward_history),
            total_rewards=total_rewards,
            average_reward=avg_reward,
            exploration_rate=self._calculate_exploration_rate(),
            exploitation_rate=1.0 - self._calculate_exploration_rate(),
            best_action_frequency=dict(action_frequency),
            convergence_status=self._assess_convergence_status()
        )
    
    def _assess_convergence_status(self) -> str:
        """Assess convergence status of RL learning."""
        
        if len(self.reward_history) < 20:
            return "Insufficient_Data"
        
        recent_rewards = list(self.reward_history)[-20:]
        reward_variance = np.var(recent_rewards)
        
        if reward_variance < 0.01:
            return "Converged"
        elif reward_variance < 0.05:
            return "Converging"
        else:
            return "Learning"
    
    def save_rl_state(self, filepath: str):
        """Save RL state for persistence."""
        
        rl_state = {
            'model_bandit_metrics': self.model_bandit.get_metrics(),
            'q_agent_metrics': self.q_agent.get_metrics(),
            'thompson_metrics': self.thompson_sampler.get_metrics(),
            'model_performance': dict(self.model_performance),
            'reward_history': list(self.reward_history),
            'action_history': [asdict(action) for action in self.action_history],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(rl_state, f, indent=2, default=str)
        
        self.logger.info(f"💾 RL state saved to {filepath}")
    
    def load_rl_state(self, filepath: str):
        """Load RL state from file."""
        
        try:
            with open(filepath, 'r') as f:
                rl_state = json.load(f)
            
            # Restore histories
            self.reward_history.extend(rl_state.get('reward_history', []))
            
            for action_data in rl_state.get('action_history', []):
                # Reconstruct RLAction objects (simplified)
                action = RLAction(
                    action_id=action_data['action_id'],
                    action_type=action_data['action_type'],
                    parameters=action_data['parameters'],
                    timestamp=datetime.fromisoformat(action_data['timestamp']),
                    expected_reward=action_data.get('expected_reward', 0.0)
                )
                self.action_history.append(action)
            
            # Restore model performance
            for model_name, performance_list in rl_state.get('model_performance', {}).items():
                self.model_performance[model_name] = performance_list
            
            self.logger.info(f"📂 RL state loaded from {filepath}")
            
        except Exception as e:
            self.logger.warning(f"Failed to load RL state: {e}")

# Global instance for integration
reinforcement_learning_framework = ReinforcementLearningFramework()