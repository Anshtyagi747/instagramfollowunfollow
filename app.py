from flask import Flask, render_template, request, jsonify
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, TwoFactorRequired
import time

app = Flask(__name__)

def fetch_usernames(client, user_ids, delay=2):
    usernames = []
    for user_id in user_ids:
        try:
            usernames.append(client.username_from_user_id(user_id))
            time.sleep(delay)  # Delay to avoid hitting rate limits
        except Exception as e:
            print(f"Error fetching username for user_id {user_id}: {e}")
    return usernames

def get_unfollowers(username, password):
    try:
        # Initialize Instagram client
        cl = Client()

        # Log in to Instagram
        cl.login(username, password)

        # Fetch followers and following
        followers = cl.user_followers(cl.user_id_from_username(username))
        following = cl.user_following(cl.user_id_from_username(username))

        # Calculate unfollowers
        followers_set = set(followers.keys())
        following_set = set(following.keys())
        unfollowers = following_set - followers_set

        # Fetch usernames for unfollowers in batches
        unfollower_usernames = fetch_usernames(cl, list(unfollowers))
        return unfollower_usernames
    
    except LoginRequired:
        return "Login failed: Please check your username and password."
    except ChallengeRequired:
        return "Instagram detected unusual login activity. Please check your Instagram app or email to verify the login."
    except TwoFactorRequired:
        return "Two-factor authentication is required. Please disable it temporarily or handle it manually."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

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
