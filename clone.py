import argparse
import requests
from requests.auth import HTTPBasicAuth
import os
import subprocess

def main():
    p = argparse.ArgumentParser('Download all GitHub repositories for a specific user')
    p.add_argument('user', type=str, help='Username')
    p.add_argument('--token', type=str, help='GitHub personal account token', required=True)
    p.add_argument('--out', type=str, help='Folder to output repositories in', required=True)
    args = p.parse_args()

    run(args.user, args.token, args.out)

def run(user, token, out):
    gh = Github(user, token)
    repos = gh.user_repos()
    i = 1
    for r in repos:
        name = r['full_name']
        url = r['clone_url']

        print('%d/%d' % (i, len(repos)), 'Processing repository', name)
        built_url = build_url(url, user, token)

        folder = os.path.join(os.path.abspath(out), name)
        if os.path.exists(folder):
            print('Folder', folder, 'exists')
            run_pull(built_url, folder)
        else:
            print('Folder', folder, 'does not exist')
            run_clone(built_url, folder, out)
        print('%d/%d' % (i, len(repos)), 'Finished processing repository', name, '\n')
        i += 1

def build_url(url, user, token):
    return url.replace('https://', 'https://%s:%s@' % (user, token))

def run_pull(url, folder):
    p = subprocess.Popen(['git', 'pull', '-r', url], cwd=folder)
    p.wait()

def run_clone(url, folder, base_folder):
    os.makedirs(folder, exist_ok=True)
    p = subprocess.Popen(['git', 'clone', url, folder], cwd=base_folder)
    p.wait()

class Github:
    USER_REPOS_URL = 'https://api.github.com/users/%s/repos'
    def __init__(self, user, token):
        self.user = user
        self.token = token

    def user_repos(self, user=None):
        output = []
        base_url = self.USER_REPOS_URL % (user or self.user)
        page = 1
        while True:
            r = requests.get('%s?page=%d' % (base_url, page), auth=HTTPBasicAuth(self.user, self.token))
            new = r.json()
            if not new:
                break
            output += new
            page += 1
        return output

if __name__ == '__main__':
    main()