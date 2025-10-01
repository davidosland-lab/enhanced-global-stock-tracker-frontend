#!/usr/bin/env python3
"""
Automatic Prompt Capture System for GitHub
Captures user prompts and saves them to the prompts folder with Git commits
"""

import os
import json
import hashlib
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
import re

class PromptCaptureSystem:
    def __init__(self, repo_path: str = "/home/user/webapp"):
        """Initialize the prompt capture system."""
        self.repo_path = repo_path
        self.prompts_dir = os.path.join(repo_path, "prompts")
        self.ensure_prompts_directory()
        
    def ensure_prompts_directory(self):
        """Ensure the prompts directory exists."""
        os.makedirs(self.prompts_dir, exist_ok=True)
        
        # Create subdirectories for organization
        for subdir in ["daily", "by_topic", "metadata"]:
            os.makedirs(os.path.join(self.prompts_dir, subdir), exist_ok=True)
    
    def generate_prompt_id(self, prompt: str) -> str:
        """Generate a unique ID for the prompt."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_obj = hashlib.md5(prompt.encode())
        short_hash = hash_obj.hexdigest()[:8]
        return f"{timestamp}_{short_hash}"
    
    def extract_topic(self, prompt: str) -> str:
        """Extract the main topic from the prompt."""
        # Simple keyword extraction - can be enhanced with NLP
        keywords = {
            "github": "github",
            "git": "version_control",
            "push": "deployment",
            "pull": "deployment",
            "commit": "version_control",
            "folder": "organization",
            "structure": "organization",
            "documentation": "documentation",
            "backend": "backend",
            "frontend": "frontend",
            "api": "api",
            "test": "testing",
            "debug": "debugging",
            "error": "troubleshooting",
            "fix": "bugfix",
            "feature": "feature",
            "refactor": "refactoring",
            "clean": "maintenance",
            "organize": "organization",
            "setup": "configuration",
            "install": "installation",
            "deploy": "deployment",
            "automatic": "automation",
            "routine": "automation",
            "capture": "monitoring",
            "save": "persistence",
            "prompt": "meta"
        }
        
        prompt_lower = prompt.lower()
        for keyword, topic in keywords.items():
            if keyword in prompt_lower:
                return topic
        return "general"
    
    def save_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Save a prompt to the filesystem with metadata."""
        prompt_id = self.generate_prompt_id(prompt)
        timestamp = datetime.now()
        topic = self.extract_topic(prompt)
        
        # Create prompt metadata
        metadata = {
            "id": prompt_id,
            "timestamp": timestamp.isoformat(),
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S"),
            "topic": topic,
            "prompt_length": len(prompt),
            "word_count": len(prompt.split()),
            "context": context or {}
        }
        
        # Save to daily folder
        daily_folder = os.path.join(self.prompts_dir, "daily", timestamp.strftime("%Y-%m-%d"))
        os.makedirs(daily_folder, exist_ok=True)
        
        daily_file = os.path.join(daily_folder, f"{prompt_id}.md")
        with open(daily_file, 'w', encoding='utf-8') as f:
            f.write(f"# Prompt: {prompt_id}\n\n")
            f.write(f"**Date**: {metadata['date']}\n")
            f.write(f"**Time**: {metadata['time']}\n")
            f.write(f"**Topic**: {metadata['topic']}\n")
            f.write(f"**Words**: {metadata['word_count']}\n\n")
            f.write("## Prompt Content\n\n")
            f.write("```\n")
            f.write(prompt)
            f.write("\n```\n\n")
            if context:
                f.write("## Context\n\n")
                f.write("```json\n")
                f.write(json.dumps(context, indent=2))
                f.write("\n```\n")
        
        # Save to topic folder
        topic_folder = os.path.join(self.prompts_dir, "by_topic", topic)
        os.makedirs(topic_folder, exist_ok=True)
        
        topic_file = os.path.join(topic_folder, f"{prompt_id}.md")
        os.symlink(daily_file, topic_file) if not os.path.exists(topic_file) else None
        
        # Save metadata
        metadata_file = os.path.join(self.prompts_dir, "metadata", f"{prompt_id}.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Update index file
        self.update_index(prompt_id, metadata)
        
        return prompt_id
    
    def update_index(self, prompt_id: str, metadata: Dict[str, Any]):
        """Update the main index file with the new prompt."""
        index_file = os.path.join(self.prompts_dir, "INDEX.md")
        
        # Read existing content if file exists
        existing_content = ""
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # If file doesn't exist or is empty, create header
        if not existing_content:
            existing_content = "# Prompt Archive Index\n\n"
            existing_content += "| Date | Time | ID | Topic | Words | Link |\n"
            existing_content += "|------|------|-----|-------|-------|------|\n"
        
        # Add new entry at the top of the table
        lines = existing_content.split('\n')
        header_end = 2  # After the header and separator
        
        new_entry = f"| {metadata['date']} | {metadata['time']} | {prompt_id} | {metadata['topic']} | {metadata['word_count']} | [View](daily/{metadata['date']}/{prompt_id}.md) |"
        
        lines.insert(header_end + 1, new_entry)
        
        # Write updated content
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def git_commit_prompt(self, prompt_id: str, topic: str):
        """Commit the new prompt to Git."""
        try:
            os.chdir(self.repo_path)
            
            # Add all files in prompts directory
            subprocess.run(['git', 'add', 'prompts/'], check=True)
            
            # Create commit message
            commit_message = f"feat(prompts): Capture prompt {prompt_id} [{topic}]\n\nAutomatically captured user prompt\nTopic: {topic}\nID: {prompt_id}"
            
            # Commit
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git commit failed: {e}")
            return False
    
    def capture_and_save(self, prompt: str, context: Optional[Dict[str, Any]] = None, auto_commit: bool = True) -> str:
        """Main method to capture and save a prompt."""
        prompt_id = self.save_prompt(prompt, context)
        topic = self.extract_topic(prompt)
        
        print(f"✅ Prompt captured: {prompt_id}")
        print(f"📁 Topic: {topic}")
        print(f"📝 Words: {len(prompt.split())}")
        
        if auto_commit:
            if self.git_commit_prompt(prompt_id, topic):
                print(f"🔄 Committed to Git")
            else:
                print(f"⚠️  Git commit failed - prompt saved locally")
        
        return prompt_id
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about captured prompts."""
        stats = {
            "total_prompts": 0,
            "topics": {},
            "daily_counts": {},
            "total_words": 0,
            "average_words": 0
        }
        
        # Count files in metadata directory
        metadata_dir = os.path.join(self.prompts_dir, "metadata")
        if os.path.exists(metadata_dir):
            for filename in os.listdir(metadata_dir):
                if filename.endswith('.json'):
                    stats["total_prompts"] += 1
                    
                    with open(os.path.join(metadata_dir, filename), 'r') as f:
                        data = json.load(f)
                        
                        # Topic statistics
                        topic = data.get("topic", "unknown")
                        stats["topics"][topic] = stats["topics"].get(topic, 0) + 1
                        
                        # Daily statistics
                        date = data.get("date", "unknown")
                        stats["daily_counts"][date] = stats["daily_counts"].get(date, 0) + 1
                        
                        # Word statistics
                        stats["total_words"] += data.get("word_count", 0)
        
        if stats["total_prompts"] > 0:
            stats["average_words"] = stats["total_words"] // stats["total_prompts"]
        
        return stats


# Example usage function
def capture_current_prompt(prompt_text: str):
    """Function to be called to capture a prompt."""
    system = PromptCaptureSystem()
    context = {
        "session": "current",
        "timestamp": datetime.now().isoformat(),
        "environment": "webapp"
    }
    return system.capture_and_save(prompt_text, context)


if __name__ == "__main__":
    # Test the system
    system = PromptCaptureSystem()
    
    # Example prompt capture
    test_prompt = "set up an automatic routine that captures each prompt and saves it to a new folder in github named prompts"
    prompt_id = system.capture_and_save(test_prompt)
    
    # Display statistics
    stats = system.get_statistics()
    print(f"\n📊 Prompt Statistics:")
    print(f"Total prompts: {stats['total_prompts']}")
    print(f"Topics: {stats['topics']}")
    print(f"Average words: {stats['average_words']}")