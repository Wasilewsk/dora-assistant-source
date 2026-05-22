from github import Github
import threading
import time
import config_manager
import os

class GitHubMonitor:
    def __init__(self, assistant):
        self.assistant = assistant
        self.github_client = None
        self.monitored_repos = []
        self.last_check_time = time.time()
        
        # Initialize client if token is available
        self.load_config()

    def load_config(self):
        settings = config_manager.load_settings()
        token = settings.get('github_token')
        if token:
            self.github_client = Github(token)
            self.monitored_repos = settings.get('github_repos', [])

    def start_monitoring(self):
        if not self.github_client:
            self.assistant.speak("GitHub token not configured.")
            return
        
        threading.Thread(target=self._monitor_loop, daemon=True).start()
        self.assistant.speak("GitHub monitoring started.")

    def _monitor_loop(self):
        while self.assistant.is_running:
            for repo_name in self.monitored_repos:
                try:
                    repo = self.github_client.get_repo(repo_name)
                    # Check for recent commits
                    commits = repo.get_commits(since=time.gmtime(self.last_check_time))
                    if commits.totalCount > 0:
                        self.assistant.speak(f"New activity in {repo_name}: {commits.totalCount} new commits.")
                except Exception as e:
                    print(f"Error checking GitHub repo {repo_name}: {e}")
            
            self.last_check_time = time.time()
            time.sleep(300) # Check every 5 minutes

def add_repository(assistant, command):
    # Simplified: extract repo from "monitor [user/repo]"
    repo = command.replace("monitor", "").strip()
    settings = config_manager.load_settings()
    repos = settings.get('github_repos', [])
    if repo not in repos:
        repos.append(repo)
        settings['github_repos'] = repos
        config_manager.save_settings(settings)
        assistant.speak(f"Now monitoring {repo}")
    else:
        assistant.speak(f"Already monitoring {repo}")
