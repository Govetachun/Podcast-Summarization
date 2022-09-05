import requests
from api_secret import API_KEY_ASSEMBLY
from api_secret import API_LISTEN_NOTE
import time
import json
import pprint


transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
assembly_headers = {'authorization': API_KEY_ASSEMBLY}


listennotes_episode_endpoint = 'https://listen-api.listennotes.com/api/v2/episodes'
listennote_headers = {'X-ListenAPI-Key': API_LISTEN_NOTE}

def get_episode_audio_url(episode_id):
    url = listennotes_episode_endpoint + '/' + episode_id
    response = requests.request('GET',url,headers = listennote_headers)

    data = response.json()
    # pprint.pprint(data)
    audio_url = data['audio']
    episode_thumb = data['thumbnail']
    podcast_title = data['podcast']['title']
    episode_title = data['title']
    
    return audio_url,episode_thumb,podcast_title,episode_title
###transcribe
def transcribe(audio_url,auto_chapters):
    transcript_request = { "audio_url": audio_url,'auto_chapters':auto_chapters}
    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=assembly_headers)
    job_id = transcript_response.json()['id']
    return job_id


###poll

def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers = assembly_headers)
    return polling_response.json()

def get_transcription_result_url(audio_url,auto_chapters):
    
    transcript_id = transcribe(audio_url,auto_chapters)
    while True:
        data =  poll(transcript_id)
        if data['status'] == 'completed':
            return data,None
        elif data['status'] == 'error':
            return data,data['error']
        
        print("waiting for 60 seconds")
        time.sleep(60)
        
    
        
def save_transcript(episode_id):
    audio_url,episode_thumb,podcast_title,episode_title= get_episode_audio_url(episode_id)
    data, error = get_transcription_result_url(audio_url,auto_chapters=True)
    pprint.pprint(data)
    if data:
        filename = episode_id + '.txt'
        with open(filename, 'w') as f:
            f.write(data['text'])

        chaptersfilename = episode_id + '_chapters.json'
        with open(chaptersfilename, 'w') as f:
            chapters = data['chapters']

            episode_data = {'chapters': chapters}
            episode_data['audio_url']=audio_url
            episode_data['episode_thumbnail']=episode_thumb
            episode_data['episode_title']=episode_title
            episode_data['podcast_title']=podcast_title
            # for key, value in kwargs.items():
            #     data[key] = value

            json.dump(episode_data, f, indent=4)
            print('Transcript saved')
            return True
    elif error:
        print("Error!!!", error)
        return False