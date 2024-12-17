from flask import Flask, render_template, request, jsonify
from instagrapi import Client
import time

app = Flask(__name__)

def fetch_usernames(client, user_ids, delay=2):
    usernames = []
    for user_id in user_ids:
        try:
            usernames.append(client.username_from_user_id(user_id))
            time.sleep(delay)
        except Exception as e:
            print(f"Error fetching username for user_id {user_id}: {e}")
    return usernames

def get_unfollowers(username, password):
    try:
        cl = Client()
        cl.login(username, password)

        followers = cl.user_followers(cl.user_id_from_username(username))
        following = cl.user_following(cl.user_id_from_username(username))

        followers_set = set(followers.keys())
        following_set = set(following.keys())
        unfollowers = following_set - followers_set

        unfollower_usernames = fetch_usernames(cl, list(unfollowers))
        return unfollower_usernames
    
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_unfollowers', methods=['POST'])
def check_unfollowers():
    username = request.form['username']
    password = request.form['password']
    unfollowers = get_unfollowers(username, password)
    
    if isinstance(unfollowers, list):
        return jsonify({'unfollowers': unfollowers})
    else:
        return jsonify({'error': unfollowers})

if __name__ == "__main__":
    app.run(debug=True)
