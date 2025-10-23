#!/usr/bin/env python3
"""
Enhanced Integrated CBA System with Neural Networks and Phase 4
================================================================
Brings together all components from GSMT-Ver-813 including:
- Phase 3: CBA Enhanced Prediction, Performance Monitoring, RL
- Phase 4: Graph Neural Networks
- Advanced Ensemble Predictor
- Neural Network Models (LSTM, GRU, Transformer)
- Deep Learning Ensemble
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Phase 3 components
try:
    from cba_enhanced_prediction_system import CBAEnhancedPredictor
    CBA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"CBA Enhanced Prediction System not available: {e}")
    CBA_AVAILABLE = False

try:
    from phase3_realtime_performance_monitoring import PerformanceMonitor
    MONITORING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Performance Monitoring not available: {e}")
    MONITORING_AVAILABLE = False

try:
    from phase3_reinforcement_learning import ReinforcementLearningOrchestrator
    RL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Reinforcement Learning not available: {e}")
    RL_AVAILABLE = False

try:
    from model_performance_backtester import ModelBacktester
    BACKTESTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Model Backtester not available: {e}")
    BACKTESTER_AVAILABLE = False

# Import advanced prediction from GSMT-Ver-813
try:
    from advanced_ensemble_predictor import (
        AdvancedEnsemblePredictor,
        PredictionResult,
        PredictionHorizon
    )
    ADVANCED_ENSEMBLE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced Ensemble Predictor not available: {e}")
    ADVANCED_ENSEMBLE_AVAILABLE = False

# Import neural network models
try:
    from neural_network_models import (
        ModelConfig,
        NeuralNetworkPredictor,
        EnsembleNeuralPredictor,
        LSTMModel,
        GRUModel,
        TransformerModel
    )
    NEURAL_NETWORKS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Neural Network Models not available: {e}")
    NEURAL_NETWORKS_AVAILABLE = False

# Import deep learning ensemble
try:
    from deep_learning_ensemble import (
        DeepEnsemblePredictor,
        UncertaintyQuantifier,
        OnlineLearningAdapter
    )
    DEEP_ENSEMBLE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Deep Learning Ensemble not available: {e}")
    DEEP_ENSEMBLE_AVAILABLE = False

# Import Phase 4 Graph Neural Networks
try:
    from phase4_graph_neural_networks import (
        GNNEnhancedPredictor,
        GNNPredictionResult,
        GNNConfig,
        GraphNeuralNetwork
    )
    GNN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Graph Neural Networks not available: {e}")
    GNN_AVAILABLE = False


class EnhancedIntegratedSystem:
    """
    Enhanced integration system combining all Phase 3, Phase 4, 
    and neural network components from GSMT-Ver-813
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 Initializing Enhanced Integrated System...")
        
        # Initialize Phase 3 components
        self.cba_predictor = CBAEnhancedPredictor() if CBA_AVAILABLE else None
        self.performance_monitor = PerformanceMonitor() if MONITORING_AVAILABLE else None
        self.rl_orchestrator = ReinforcementLearningOrchestrator() if RL_AVAILABLE else None
        self.backtester = ModelBacktester() if BACKTESTER_AVAILABLE else None
        
        # Initialize advanced prediction from GSMT-Ver-813
        self.advanced_predictor = AdvancedEnsemblePredictor() if ADVANCED_ENSEMBLE_AVAILABLE else None
        
        # Initialize neural network components
        if NEURAL_NETWORKS_AVAILABLE:
            self.neural_config = ModelConfig()
            self.lstm_predictor = NeuralNetworkPredictor(model_type='lstm', config=self.neural_config)
            self.gru_predictor = NeuralNetworkPredictor(model_type='gru', config=self.neural_config)
            self.transformer_predictor = NeuralNetworkPredictor(model_type='transformer', config=self.neural_config)
            self.ensemble_neural = EnsembleNeuralPredictor(['lstm', 'gru', 'transformer'])
        else:
            self.neural_config = None
            self.lstm_predictor = None
            self.gru_predictor = None
            self.transformer_predictor = None
            self.ensemble_neural = None
        
        # Initialize deep learning ensemble
        if DEEP_ENSEMBLE_AVAILABLE and NEURAL_NETWORKS_AVAILABLE:
            self.deep_ensemble = DeepEnsemblePredictor(config=self.neural_config)
            self.uncertainty_quantifier = UncertaintyQuantifier()
        else:
            self.deep_ensemble = None
            self.uncertainty_quantifier = None
        
        # Initialize Phase 4 Graph Neural Networks
        if GNN_AVAILABLE:
            self.gnn_config = GNNConfig()
            self.gnn_predictor = GNNEnhancedPredictor(config=self.gnn_config)
        else:
            self.gnn_config = None
            self.gnn_predictor = None
        
        self._log_initialization_status()
    
    def _log_initialization_status(self):
        """Log the initialization status of all components"""
        self.logger.info("✅ Component Initialization Status:")
        self.logger.info(f"  Phase 3 CBA: {'✅' if CBA_AVAILABLE else '❌'}")
        self.logger.info(f"  Phase 3 Monitoring: {'✅' if MONITORING_AVAILABLE else '❌'}")
        self.logger.info(f"  Phase 3 RL: {'✅' if RL_AVAILABLE else '❌'}")
        self.logger.info(f"  Backtester: {'✅' if BACKTESTER_AVAILABLE else '❌'}")
        self.logger.info(f"  Advanced Ensemble: {'✅' if ADVANCED_ENSEMBLE_AVAILABLE else '❌'}")
        self.logger.info(f"  Neural Networks: {'✅' if NEURAL_NETWORKS_AVAILABLE else '❌'}")
        self.logger.info(f"  Deep Ensemble: {'✅' if DEEP_ENSEMBLE_AVAILABLE else '❌'}")
        self.logger.info(f"  Phase 4 GNN: {'✅' if GNN_AVAILABLE else '❌'}")
    
    async def get_comprehensive_prediction(self, symbol: str, timeframe: str = "5d") -> Dict[str, Any]:
        """
        Get comprehensive prediction from all available components
        """
        self.logger.info(f"📊 Generating comprehensive prediction for {symbol} ({timeframe})")
        
        results = {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }
        
        # Phase 3 CBA Analysis
        if self.cba_predictor:
            try:
                cba_result = await self.cba_predictor.analyze_cba_comprehensive(symbol)
                results['components']['cba_analysis'] = {
                    'publications_count': len(cba_result.publications) if hasattr(cba_result, 'publications') else 0,
                    'news_count': len(cba_result.news_articles) if hasattr(cba_result, 'news_articles') else 0,
                    'sentiment_score': cba_result.sentiment_score if hasattr(cba_result, 'sentiment_score') else None,
                    'prediction': cba_result.prediction if hasattr(cba_result, 'prediction') else None
                }
                self.logger.info("  ✅ CBA analysis complete")
            except Exception as e:
                self.logger.warning(f"  ⚠️ CBA analysis failed: {e}")
                results['components']['cba_analysis'] = {'error': str(e)}
        
        # Advanced Ensemble Prediction
        if self.advanced_predictor:
            try:
                advanced_result = await self.advanced_predictor.generate_advanced_prediction(
                    symbol=symbol,
                    timeframe=timeframe,
                    external_factors={
                        'social_sentiment': 0.1,
                        'news_sentiment': 0.05,
                        'geopolitical_risk': 0.2,
                        'global_volatility': 0.15
                    }
                )
                results['components']['advanced_ensemble'] = {
                    'direction': advanced_result.direction,
                    'expected_return': advanced_result.expected_return,
                    'confidence_interval': advanced_result.confidence_interval,
                    'probability_up': advanced_result.probability_up,
                    'volatility_estimate': advanced_result.volatility_estimate,
                    'risk_adjusted_return': advanced_result.risk_adjusted_return,
                    'uncertainty_score': advanced_result.uncertainty_score
                }
                self.logger.info("  ✅ Advanced ensemble prediction complete")
            except Exception as e:
                self.logger.warning(f"  ⚠️ Advanced ensemble failed: {e}")
                results['components']['advanced_ensemble'] = {'error': str(e)}
        
        # Phase 4 Graph Neural Network
        if self.gnn_predictor:
            try:
                gnn_result = await self.gnn_predictor.generate_gnn_enhanced_prediction(
                    symbol=symbol,
                    timeframe=timeframe,
                    include_graph_analysis=True
                )
                results['components']['graph_neural_network'] = {
                    'predicted_price': gnn_result.predicted_price,
                    'confidence_score': gnn_result.confidence_score,
                    'node_importance': gnn_result.node_importance,
                    'graph_centrality': gnn_result.graph_centrality,
                    'sector_influence': gnn_result.sector_influence,
                    'market_influence': gnn_result.market_influence,
                    'systemic_risk_score': gnn_result.systemic_risk_score,
                    'key_relationships': gnn_result.key_relationships[:3] if gnn_result.key_relationships else []
                }
                self.logger.info("  ✅ Graph Neural Network prediction complete")
            except Exception as e:
                self.logger.warning(f"  ⚠️ GNN prediction failed: {e}")
                results['components']['graph_neural_network'] = {'error': str(e)}
        
        # Neural Network Ensemble (if data available)
        if self.ensemble_neural:
            try:
                # Generate sample data for neural networks (in production, use real data)
                sample_data = self._generate_sample_data(symbol)
                nn_results = await self.get_neural_network_predictions(symbol, sample_data)
                results['components']['neural_networks'] = nn_results
                self.logger.info("  ✅ Neural network predictions complete")
            except Exception as e:
                self.logger.warning(f"  ⚠️ Neural network predictions failed: {e}")
                results['components']['neural_networks'] = {'error': str(e)}
        
        # Performance Metrics
        if self.performance_monitor:
            try:
                metrics = self.performance_monitor.get_current_metrics()
                results['components']['performance_metrics'] = metrics
                self.logger.info("  ✅ Performance metrics retrieved")
            except Exception as e:
                self.logger.warning(f"  ⚠️ Performance metrics failed: {e}")
                results['components']['performance_metrics'] = {'error': str(e)}
        
        # Aggregate predictions
        results['aggregate'] = self._aggregate_predictions(results['components'])
        
        return results
    
    def _generate_sample_data(self, symbol: str) -> pd.DataFrame:
        """Generate sample data for neural network testing"""
        # In production, this would fetch real market data
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        data = pd.DataFrame({
            'Open': np.random.normal(100, 10, 100),
            'High': np.random.normal(105, 10, 100),
            'Low': np.random.normal(95, 10, 100),
            'Close': np.random.normal(100, 10, 100),
            'Volume': np.random.uniform(1000000, 5000000, 100)
        }, index=dates)
        return data
    
    async def get_neural_network_predictions(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Get predictions from all neural network models"""
        results = {}
        
        if not NEURAL_NETWORKS_AVAILABLE or len(data) < self.neural_config.sequence_length:
            return {'error': 'Insufficient data or neural networks not available'}
        
        try:
            feature_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            features = data[feature_cols].values
            
            # Individual neural network predictions
            if self.lstm_predictor:
                lstm_pred = self.lstm_predictor.predict(features)
                results['lstm'] = float(lstm_pred[-1]) if len(lstm_pred) > 0 else None
            
            if self.gru_predictor:
                gru_pred = self.gru_predictor.predict(features)
                results['gru'] = float(gru_pred[-1]) if len(gru_pred) > 0 else None
            
            if self.transformer_predictor:
                transformer_pred = self.transformer_predictor.predict(features)
                results['transformer'] = float(transformer_pred[-1]) if len(transformer_pred) > 0 else None
            
            # Ensemble prediction
            if self.ensemble_neural:
                ensemble_pred = self.ensemble_neural.predict_ensemble(features, method='weighted')
                results['ensemble'] = float(ensemble_pred[-1]) if len(ensemble_pred) > 0 else None
            
            # Deep ensemble with uncertainty
            if self.deep_ensemble:
                import torch
                deep_pred_tensor = torch.FloatTensor(features).unsqueeze(0)
                deep_pred, uncertainty = self.deep_ensemble.predict_with_uncertainty(deep_pred_tensor)
                results['deep_ensemble'] = {
                    'prediction': float(deep_pred[0, 0]),
                    'uncertainty': float(uncertainty[0, 0])
                }
                
        except Exception as e:
            self.logger.error(f"Neural network predictions failed: {e}")
            results['error'] = str(e)
        
        return results
    
    def _aggregate_predictions(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate predictions from all components"""
        aggregate = {
            'consensus_direction': None,
            'average_confidence': None,
            'risk_level': None,
            'recommendation': None
        }
        
        directions = []
        confidences = []
        
        # Collect directions and confidences
        if 'advanced_ensemble' in components and 'error' not in components['advanced_ensemble']:
            ae = components['advanced_ensemble']
            directions.append(ae.get('direction'))
            confidences.append(1 - ae.get('uncertainty_score', 0.5))
        
        if 'graph_neural_network' in components and 'error' not in components['graph_neural_network']:
            gnn = components['graph_neural_network']
            confidences.append(gnn.get('confidence_score', 0.5))
            # Infer direction from predicted price (simplified)
            if 'predicted_price' in gnn:
                directions.append('up' if gnn['predicted_price'] > 100 else 'down')
        
        # Calculate consensus
        if directions:
            up_count = directions.count('up')
            down_count = directions.count('down')
            if up_count > down_count:
                aggregate['consensus_direction'] = 'up'
            elif down_count > up_count:
                aggregate['consensus_direction'] = 'down'
            else:
                aggregate['consensus_direction'] = 'sideways'
        
        if confidences:
            aggregate['average_confidence'] = np.mean(confidences)
        
        # Determine risk level
        if 'graph_neural_network' in components and 'systemic_risk_score' in components['graph_neural_network']:
            risk_score = components['graph_neural_network']['systemic_risk_score']
            if risk_score < 0.3:
                aggregate['risk_level'] = 'low'
            elif risk_score < 0.7:
                aggregate['risk_level'] = 'medium'
            else:
                aggregate['risk_level'] = 'high'
        
        # Generate recommendation
        if aggregate['consensus_direction'] and aggregate['average_confidence']:
            if aggregate['average_confidence'] > 0.7 and aggregate['consensus_direction'] == 'up':
                aggregate['recommendation'] = 'strong_buy'
            elif aggregate['average_confidence'] > 0.5 and aggregate['consensus_direction'] == 'up':
                aggregate['recommendation'] = 'buy'
            elif aggregate['average_confidence'] > 0.7 and aggregate['consensus_direction'] == 'down':
                aggregate['recommendation'] = 'strong_sell'
            elif aggregate['average_confidence'] > 0.5 and aggregate['consensus_direction'] == 'down':
                aggregate['recommendation'] = 'sell'
            else:
                aggregate['recommendation'] = 'hold'
        
        return aggregate
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all system components"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'components': {
                'phase3_cba': 'operational' if CBA_AVAILABLE else 'unavailable',
                'phase3_monitoring': 'operational' if MONITORING_AVAILABLE else 'unavailable',
                'phase3_rl': 'operational' if RL_AVAILABLE else 'unavailable',
                'backtester': 'operational' if BACKTESTER_AVAILABLE else 'unavailable',
                'advanced_ensemble': 'operational' if ADVANCED_ENSEMBLE_AVAILABLE else 'unavailable',
                'neural_networks': 'operational' if NEURAL_NETWORKS_AVAILABLE else 'unavailable',
                'deep_ensemble': 'operational' if DEEP_ENSEMBLE_AVAILABLE else 'unavailable',
                'phase4_gnn': 'operational' if GNN_AVAILABLE else 'unavailable'
            }
        }
        
        # Add GNN status if available
        if self.gnn_predictor:
            status['gnn_details'] = self.gnn_predictor.get_system_status()
        
        return status


# Create global instance
enhanced_system = EnhancedIntegratedSystem()

# Test function
async def test_enhanced_system():
    """Test the enhanced integrated system"""
    print("🚀 Testing Enhanced Integrated System")
    print("=" * 50)
    
    # Get system status
    status = enhanced_system.get_system_status()
    print("\n📊 System Status:")
    for component, state in status['components'].items():
        emoji = "✅" if state == "operational" else "❌"
        print(f"  {emoji} {component}: {state}")
    
    # Test comprehensive prediction
    test_symbols = ['CBA.AX', 'AAPL', '^AORD']
    for symbol in test_symbols:
        print(f"\n📈 Testing comprehensive prediction for {symbol}...")
        result = await enhanced_system.get_comprehensive_prediction(symbol)
        
        # Display results
        if 'aggregate' in result:
            agg = result['aggregate']
            print(f"  Consensus Direction: {agg.get('consensus_direction', 'N/A')}")
            print(f"  Average Confidence: {agg.get('average_confidence', 0):.2%}")
            print(f"  Risk Level: {agg.get('risk_level', 'N/A')}")
            print(f"  Recommendation: {agg.get('recommendation', 'N/A')}")
        
        # Show component results
        print("\n  Component Results:")
        for component, data in result.get('components', {}).items():
            if isinstance(data, dict) and 'error' not in data:
                print(f"    ✅ {component}: Available")
            else:
                print(f"    ⚠️ {component}: Error or unavailable")
    
    print("\n✅ Enhanced system testing completed!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_system())