#!/usr/bin/python3

import requests
import json
import os
import sys
import argparse

parser = argparse.ArgumentParser(description="Download all Github repos for a specified user.")
parser.add_argument('username', type=str, help="All repos published by this username will be cloned.")
parser.add_argument('-t' , '--testing', action='store_true', help="Output the git clone commands but don't execute them.")
parser.add_argument('-n', '--no-metadata-save', action='store_true', help="Don't locally save metadata (JSON) files for Github API responses.")
parser.add_argument('-s', '--skip-cwd-check', action='store_true', help="Use the current working directory for cloning directly into, even if there are apparently unrelated files present.")
parser.add_argument('-j', '--json-files', type=str, nargs='*', metavar="FILE", help="Use one or more local json files instead of making API requests.")
args = parser.parse_args()
args_vars = vars(args)

testing_mode = False
user_to_clone = ""
use_local_json_files = False
user_provided_json_files_list = []
save_github_json_metadata = True
skip_cwd_check = False
max_per_json=100

def get_repos_json_url(user=user_to_clone, per_page=max_per_json, page=1):
    if user_to_clone and not user:
        user = user_to_clone
    return "https://api.github.com/users/" + user + "/repos?per_page=" + str(per_page) + "&page=" + str(page)

def get_repos_json_filename(user=user_to_clone, page=1):
    if user_to_clone and not user:
        user = user_to_clone
    default_filename = user + '-repos-page' + str(page) + '.json'
    if use_local_json_files:
        if len(user_provided_json_files_list) > 0:
            if (user_provided_json_files_list[page - 1]):
                return user_provided_json_files_list[page - 1]
            else:
                return False
        else:
            if (os.path.exists(default_filename)):
                return default_filename
            else:
                return False
    return default_filename

def get_json_page_num(page_num):
    url = get_repos_json_url(user=user_to_clone, page=page_num)
    response = requests.get(url)
    return response

def get_all_repos_list():
    all_repos = []
    can_continue = True
    if (use_local_json_files):
        json_files_list = []
        if len(user_provided_json_files_list) > 0:
            json_files_list = user_provided_json_files_list
        else:
            page = 0
            while can_continue:
                page += 1
                filename = get_repos_json_filename(page=page)
                if (filename):
                    json_files_list.append(filename)
                else:
                    can_continue = False
        for filename in user_provided_json_files_list:
            with open(filename, 'r') as repo_file:
                all_repos = all_repos + json.load(repo_file)
        return all_repos
    page_num = 0
    while (can_continue):
        page_num += 1
        response = get_json_page_num(page_num)
        if (response.status_code != 200):
            can_continue = False
        repos_json = response.json()
        if save_github_json_metadata:
            filename_to_save = get_repos_json_filename(user=user_to_clone, page=page_num)
            with open(filename_to_save, 'w', encoding='utf-8') as f:
                json.dump(repos_json, f, ensure_ascii=False, indent=4)
        all_repos = all_repos + repos_json
        if len(repos_json) < max_per_json:
            can_continue = False
    return all_repos

def prepare_working_directory():
    if (skip_cwd_check):
        print ("Skipping check of working directory. Will use working directory to clone repos into.")
        return
    dir = os.listdir('.')
    if len(dir) != 0:
        print("Current working directory is not empty.")
        if (not os.path.exists(get_repos_json_filename(user=user_to_clone))):
            print ("Current working directory does not appear to have Github API metadata files present. Creating subdirectory to use for cloning into.")
            os.makedirs(user_to_clone, exist_ok=True)
            os.chdir(user_to_clone)
    else:
        print("Working directory is empty and will be used to clone into.")

def clone_all_repos():
    repos = get_all_repos_list()
    prepare_working_directory()
    for repo in repos:
        clone_command = 'git clone ' + repo['clone_url']
        print (clone_command)
        if (not testing_mode):
            git_output = os.popen(clone_command).read()
            print (git_output)
            print ("")

def handle_runtime_arguments():
    global user_to_clone
    global testing_mode
    global use_local_json_files
    global user_provided_json_files_list
    global save_github_json_metadata
    global skip_cwd_check
    user_to_clone = getattr(args, 'username')
    testing_mode = getattr(args, 'testing')
    json_files = getattr(args, 'json_files')
    if isinstance(json_files, list):
        use_local_json_files = True
        if len(json_files) > 0:
            user_provided_json_files_list = json_files
    save_github_json_metadata = not getattr(args, 'no_metadata_save')
    skip_cwd_check = getattr(args, 'skip_cwd_check')

print(args)
handle_runtime_arguments()
print ("Cloning all repos of Github user: " + user_to_clone)
print ("Testing mode?: " + str(testing_mode))
print ("Use local json file instead of Github API calls?: " + str(use_local_json_files))
print ("Save metadata from Github API calls?: " + str(save_github_json_metadata))
print ("Skip checking current working directory for unrelated files?: " + str(skip_cwd_check))
print ("")
clone_all_repos()
