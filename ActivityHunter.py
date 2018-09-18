""" CONSTANTS """
BASE_URL = 'https://www.instagram.com/'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
STORIES_UA = 'Instagram 52.0.0.8.83 (iPhone; CPU iPhone OS 11_4 like Mac OS X; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/605.1.15'
CHROME_WIN_UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
IMG_FEED = BASE_URL +  'graphql/query/?query_hash=e7e2f4da4b02303f74f0841279e52d76&variables=%7B%22id%22%3A%2254113000%22%2C%22first%22%3A50%2C%22after%22%3A%22'
FOLLOWS_FIRST_URL = BASE_URL + 'graphql/query/?query_hash=c56ee0ae1f89cdbd1c89e2bc6b8f3d18&variables=%7B%22id%22%3A%22{0}%22%2C%22include_reel%22%3Atrue%2C%22first%22%3A50%7D'
FOLLOWS_URL = BASE_URL + 'graphql/query/?query_hash=c56ee0ae1f89cdbd1c89e2bc6b8f3d18&variables=%7B%22id%22%3A%22{0}%22%2C%22include_reel%22%3Afalse%2C%22first%22%3A50%2C%22after%22%3A%22{1}%22%7D'
TIMELINE_URL = BASE_URL + 'graphql/query/?query_hash=a5164aed103f24b03e7b7747a2d94e3c&variables='
TIMELINE_VARS = '{{"id":"{0}","first":50,"after":"{1}"}}'
LIKES_URL = BASE_URL + 'graphql/query/?query_hash=e0f59e4a1c8d78d0161873bc2ee7ec44&variables='
LIKES_VARS = '{{"shortcode":"{0}","include_reel":true,"first":50,"after":"{1}"}}'
COMMENTS_URL = BASE_URL + 'graphql/query/?query_hash=f0986789a5c5d17c2400faebf16efd0d&variables='
COMMENTS_VAR = '{{"shortcode":"{0}","first":50,"after":"{1}"}}'
SLEEP_IN_SECONDS = 1
TRY_AGAIN_SLEEP_DELAY = 3000
USERNAME = ''
PASSWORD = ''


""" IMPORTS """
import requests, json, time, hashlib, sys, datetime, argparse


class ActivityHunter:
    
    def __init__(self, target_user, from_users):
        self.comments = True
        self.likes = True
        self.tag = True
        self.sharedData = ''
        self.target_user = target_user
        self.to_date = "06/10/2014"
        self.from_date = 0  
        self.time_interval = False
        self.from_users = from_users
        self.num_of_fetches = 0        
        self.time_from = ""         
        self.log_in = False
        self.NUM_OF_FETCHES = 0 
        
        
        self.to_date = time.mktime(datetime.datetime.strptime(self.to_date, "%d-%m-%Y").timetuple())
        
    
    #Logs in to Instagram
    def login(self):
        self.session = requests.Session()
        self.session.headers = {'user-agent': CHROME_WIN_UA}
        self.session.cookies.set('ig_pr', '1')             
        self.session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
        
        if self.log_in:
            #Add login settings if option is true
            req = self.session.get(BASE_URL)
            self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
            
            login_data = {'username': USERNAME, 'password': PASSWORD}
            login = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)
            self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
            self.cookies = login.cookies
            response = json.loads(login.text)
            
            if not response.get('user'):
                print('No such username or verification problem')
            elif response.get('user') and response.get('authenticated') is False :
                print('Wrong password')
            else:
                print('Login successful')
                self.is_logged_in = True   
    
        
    def to_json(self, data):
        self.NUM_OF_FETCHES +=1
        print(self.NUM_OF_FETCHES)
        #Universal sleep for all functions that fetches data from Instagram
        time.sleep(SLEEP_IN_SECONDS)
        
        return json.loads(data)
    
    def _gen_query_graphql(self, url, url_vars, media_id, end_cursor = ""):
        endpoint_url = url + url_vars     
        while True:
            #update gis-cookie (req. for no-login scraping)
            params = url_vars.format(media_id, end_cursor)   
            self.update_ig_gis_header(params)    
            
            edges, has_next_page, end_cursor = self._data_request(endpoint_url.format(media_id, end_cursor), media_id)

            for edge in edges:
                yield edge['node']
                                                   
            if has_next_page:
             #If data on next page, continue                                                                 
                 continue
            else:
                break
                  
    def scrape(self):   
        print("Scraping...")
        for user in self.from_users:
            self.query_timeline(user)
        print('DONE')
        
    
    def query_timeline(self, username): 
        for media in self._gen_query_graphql(TIMELINE_URL, TIMELINE_VARS, self.get_user_id(username)):

            if self.time_interval:
                #Break if media is timestamp is lower than lowest interval span
                if self.from_date > media['taken_at_timestamp']:
                    break
                #Go to next media if it's not in selected interval. 
                if not self.from_date <= media['taken_at_timestamp'] <= self.to_date:
                    continue
            
            if self.tag:
                for tagged_user in media['edge_media_to_tagged_user']['edges']:
                    if tagged_user['node']['user']['username'] in self.target_user:
                        print("user tagged in photo")
                        
                       
            #Check if likes enable in settings and likes exist in post
            if self.likes and media['edge_media_preview_like']['count']:
                    for likes in self._gen_query_graphql(LIKES_URL, LIKES_VARS, media['shortcode']):
                        if likes['username'] in self.target_user:                          
                            print(likes['username']+" liked "+username+"'s media(")
                            break
            
            if self.comments:
                comment_preview_edges = media['edge_media_to_comment']['edges']
                has_next_page = media['edge_media_to_comment']['page_info']['has_next_page']
                shortcode = media['shortcode']   
                
                #Check if comments exist in post
                if comment_preview_edges:
                    #If post has less comments than preview, scrape direct from media, otherwise scrape from post
                    for comments in self._gen_query_graphql(COMMENTS_URL, COMMENTS_VAR, shortcode) if has_next_page else [a['node'] for a in comment_preview_edges]:
                        if comments['owner']['username'] in self.target_user:
                            print(comments['text'])
                        
                        
    #Function that get response data from Instagram
    #Return JSON
    def _data_request(self, data_url, media_id):
        while(True):
            response = self.session.get(data_url)        
            response = self.to_json(response.text)
                     
            try:
                #TIMELINE
                if 'a5164aed103f24b03e7b7747a2d94e3c' in data_url:
                    end_cursor = response['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
                    has_next_page = response['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'] 
                    edges = response['data']['user']['edge_owner_to_timeline_media']['edges']   
                    
                #LIKES
                elif 'e0f59e4a1c8d78d0161873bc2ee7ec44' in data_url:                   
                    end_cursor = response['data']['shortcode_media']['edge_liked_by']['page_info']['end_cursor']  
                    has_next_page = response['data']['shortcode_media']['edge_liked_by']['page_info']['has_next_page']   
                    edges = response['data']['shortcode_media']['edge_liked_by']['edges']
                    
                #COMMENTS
                elif 'f0986789a5c5d17c2400faebf16efd0d' in data_url:
                   end_cursor = response['data'] ['shortcode_media']['edge_media_to_comment']['page_info']['end_cursor'] 
                   has_next_page = response['data']['shortcode_media']['edge_media_to_comment']['page_info']['has_next_page']  
                   edges = response['data']['shortcode_media']['edge_media_to_comment']['edges']
                                   
                return edges, has_next_page, end_cursor
                
            #If reached KeyError, probably reached request limit
            except KeyError as e:
                if  'rate limited' in response['message']:
                    print('reached maximum rate limit.. trying again in '+str(TRY_AGAIN_SLEEP_DELAY)+" sec")
                    time.sleep(TRY_AGAIN_SLEEP_DELAY)
                else:
                    print(response)
                               
                
    def get_ig_gis(self, rhx_gis, params):
        data = rhx_gis + ":" + params
        if sys.version_info.major >= 3:
            return hashlib.md5(data.encode('utf-8')).hexdigest()
        else:
            return hashlib.md5(data).hexdigest()

    def update_ig_gis_header(self, params):
        self.session.headers.update({
            'x-instagram-gis': self.get_ig_gis(
                self.rhx_gis,
                params
            )
            })      
            
               
    #Get user ID of user
    def get_user_id(self, username):
        if self.sharedData is '' or self.get_sharedData(username)['entry_data']['ProfilePage'][0]['graphql']['user']['id'] is not username:
            return self.get_sharedData(username)['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        else:
            return username
        
    #Parse sharedData from source code
    #sharedData is needed for grabbing IDs etc
    def get_sharedData(self, username):     
        response = self.session.get(BASE_URL+username)      
        sharedData = self.to_json(response.text.split("window._sharedData = ")[1].split(";</script>")[0])   
        self.sharedData = sharedData        
        #Update rhx_gis
        self.set_rhx_gis(self.sharedData['rhx_gis'])        
        return sharedData
        
    
    def set_rhx_gis(self, rhx_gis):
        self.rhx_gis = rhx_gis


def main():
    parser = argparse.ArgumentParser(description='Activity Hunter')
    parser.add_argument('--target',"-t", help='Track activity on this Instagram username')
    parser.add_argument('')
    
    
    
    a = ActivityHunter('target',['usernames'])
    a.login()
    a.scrape()

    
    

if __name__ == '__main__':
    main()