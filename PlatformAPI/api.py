from typing import Union

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from pydantic import BaseModel
from typing import Literal
import time
import uuid
import os
import shutil

import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud import storage

from vikit.video.video import Video, VideoBuildSettings
from vikit.video.imported_video import ImportedVideo
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.raw_image_based_video import RawImageBasedVideo
from vikit.video.composite_video import CompositeVideo
from vikit.video.seine_transition import SeineTransition
from vikit.prompt.prompt_factory import PromptFactory
from vikit.common.context_managers import WorkingFolderContext
from vikit.music_building_context import MusicBuildingContext
import vikit.common.config as config

logger.add("log.txt")

working_folder=os.getcwd() + "/outputs/"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getcwd() + "/gcpkey.json"
cred = credentials.Certificate(os.getcwd() + '/aivideoproject-0ddbb366ce3e.json')


os.chdir(working_folder)

app = firebase_admin.initialize_app(cred)

db = firestore.client()


class Item(BaseModel):
    vikit_api_key: str
    video_per_Second: int = 2 #not implemented yet
    model: Literal["videocrafter", "stabilityai", "haiper"] = "videocrafter"
    include_read_aloud_prompt: bool = True
    generate_background_music: bool= False
    prompt: str

class RetrieveVideos(BaseModel):
    vikit_api_key: str
    maxTimestamp: int
  

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/getvideos")
async def retrieve_videos(item: RetrieveVideos):
    users_ref = db.collection("users").where(filter=FieldFilter("vikitAPIKey", "==", item.vikit_api_key)).stream()
    try:
        userDocument = next(users_ref)
    except:
        return "The Vikit API Key is not valid"
    email = userDocument.to_dict()['email']
    generations = db.collection("apiGenerations").where(filter=FieldFilter("email", "==", email)).order_by("timestamp", direction=firestore.Query.DESCENDING).start_at({"timestamp": item.maxTimestamp}).limit(50).get()
    returnedGenerations = []
    for doc_item in generations:
        returnedGenerations.append(doc_item.to_dict())
    return returnedGenerations
    print(returnedGenerations)
    return returnedGenerations

@app.post("/createvideo/")
async def create_item(item: Item):
    negative_prompt = """bad anatomy, bad hands, missing fingers, extra fingers, three hands, three legs, bad arms, missing legs, missing arms, poorly drawn face, bad face, fused face, cloned face, three crus, fused feet, fused thigh, extra crus, ugly fingers, amputation, disconnected limbs, cartoonish"""
    os.chdir(working_folder)
    # users_ref = db.collection("users").where(filter=FieldFilter("vikitAPIKey", "==", item.vikit_api_key)).stream()
    try:
        users_ref = db.collection("users").where(filter=FieldFilter("vikitAPIKey", "==", item.vikit_api_key)).stream()
        userDocument = next(users_ref)
   # except:
    #    return "The Vikit API Key is not valid"
    
    except StopIteration:
        # This exception occurs if the query does not return any documents
        logger.error("The Vikit API Key is not valid or no user found for the provided API key.")
        raise HTTPException(status_code=404, detail="The Vikit API Key is not valid or no user found.")
    
    except Exception as e:
        # Handle any other exceptions that may occur
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
    
    email = userDocument.to_dict()['email']
    fileName = email + "_" + str(time.time())

    sent_prompt = item.prompt
    prompt_word_count = len(sent_prompt.split())

    if prompt_word_count < 2:
        print("Prompt has less than 2 words, stopping the process. Please enter a prompt of more than 2 words.")
        logger.error("Prompt has less than 2 words, stopping the process. Please enter a prompt of more than 2 words.")
        return "Prompt has less than 2 words, stopping the process. Please enter a prompt of more than 2 words."
    
    generation_id = str(uuid.uuid4())
    progress = 0
    firestoreEntry = {"email": email, "prompt": item.prompt, "progress": progress, "state": "Processing", "timestamp": time.time()}
    db.collection("apiGenerations").document(generation_id).set(firestoreEntry)
    try:
      #Generation model dependent parameters
      interpolate=False
      parrallelDoubleVideos = 5
      if item.model == "videocrafter":
          interpolate=True
          parrallelDoubleVideos=15
  
      with WorkingFolderContext(working_folder):
      
          video_build_settings = VideoBuildSettings(
              music_building_context=MusicBuildingContext(
                  apply_background_music=False,
                  generate_background_music=False,
              ),
              test_mode=False,
              include_read_aloud_prompt=False,
              target_model_provider="videocrafter",
              output_video_file_name=fileName + ".mp4",
              cascade_build_settings=False,
              interpolate=False,
              target_dir_path=working_folder,
              vikit_api_key=item.vikit_api_key
          )
      
          #We divide the input text in chunks in order to prevent sending to much parrallel calls to the GenAI Video backends
          promptText = item.prompt
        
          gw = video_build_settings.get_ml_models_gateway()
          prompt = await PromptFactory(ml_gateway=gw).create_prompt_from_text(promptText)
          allSubs = []
          currentSubSubs = []
          currentIndex = 0
      
          for sub in prompt.subtitles:
              currentSubSubs.append(sub.text)
              currentIndex += 1
              if currentIndex == parrallelDoubleVideos: # Most of video backends do not accept more than 20 parrallel video generation, we want to generate 2 videos per subtitle, and have a safety margin
                  allSubs.append(currentSubSubs)
                  currentSubSubs = []
                  currentIndex = 0
          
          if len(currentSubSubs) != 0:
              allSubs.append(currentSubSubs)
      
      
          vid_cp_final = CompositeVideo()
          vid_cp_final._is_root_video_composite = True
          #For each of these chunks, we generate a video in parrallel
          index=0
          totalSubstitles = len(allSubs)
          for subtitlesGroup in allSubs:
      
              #We define intermediary build settings for our sub video
              video_build_settings_intermediary = VideoBuildSettings(
                  music_building_context=MusicBuildingContext(
                      apply_background_music=item.generate_background_music,
                      generate_background_music=item.generate_background_music,
                  ),
                  test_mode=False,
                  include_read_aloud_prompt=item.include_read_aloud_prompt,
                  target_model_provider=item.model,
                  output_video_file_name=fileName + "_" + str(index) + ".mp4",
                  interpolate=interpolate,
                  cascade_build_settings=False,
                  target_dir_path=working_folder,
                  vikit_api_key=item.vikit_api_key
              )
              gw = video_build_settings.get_ml_models_gateway()
              textToBeSaid = ' '.join(subtitlesGroup)
              prompt = await PromptFactory(ml_gateway=gw).create_prompt_from_text(textToBeSaid)
              prompt.negative_prompt = negative_prompt
              video_build_settings_intermediary.prompt = prompt
  
              video_build_settings_raw_video = VideoBuildSettings(
                  music_building_context=MusicBuildingContext(
                      apply_background_music=False,
                      generate_background_music=False,
                  ),
                  test_mode=False,
                  include_read_aloud_prompt=False,
                  target_model_provider=item.model,
                  output_video_file_name="Output_" + str(index) + ".mp4",
                  interpolate=False,
                  vikit_api_key=item.vikit_api_key
              )
  
            
              vid_cp_intermediary = CompositeVideo()
              for sub in prompt.subtitles:
                  keyword_based_vid1 = RawTextBasedVideo(sub.text + ",4k rendering, High quality faces, natural beautiful faces")
                
                  keyword_based_vid2 = RawTextBasedVideo(sub.text + ",4k rendering, High quality faces, natural beautiful faces")
                
                  vid_cp_intermediary.append_video(keyword_based_vid1).append_video(keyword_based_vid2)
              await vid_cp_intermediary.build(build_settings=video_build_settings_intermediary)
              vid_cp_final.append_video(vid_cp_intermediary)
      
              index = index + 1
  
              firestoreEntry["progress"] = int(100*index/(totalSubstitles+1))
              db.collection("apiGenerations").document(generation_id).set(firestoreEntry)
            
          await vid_cp_final.build(build_settings=video_build_settings)
          print(f"Saved video {vid_cp_final.media_url}")
      
  
      # Instantiates a client
      storage_client = storage.Client()
      bucket = storage_client.bucket("aivideoscreated")
      blob = bucket.blob(fileName + ".mp4")
      blob.upload_from_filename(working_folder + vid_cp_final.media_url)
      
      print("URL : https://storage.googleapis.com/aivideoscreated/" + fileName + ".mp4")
      firestoreEntry["state"] = "Completed"
      firestoreEntry["progress"] = 100
      firestoreEntry["url"] = "https://storage.googleapis.com/aivideoscreated/" + fileName + ".mp4"
      db.collection("apiGenerations").document(generation_id).set(firestoreEntry)
  
      #Send email
      import sib_api_v3_sdk
      from sib_api_v3_sdk.rest import ApiException
  
      configuration = sib_api_v3_sdk.Configuration()
      configuration.api_key["api-key"] = (
          ""
      )
  
  
      api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
          sib_api_v3_sdk.ApiClient(configuration)
      )
      subject = "Vikit.ai - Your AI generated video"
      html_content = (
          "<html><body><h1>Your AI Generated video is ready</h1><h3>You can download it here : <a href='https://storage.googleapis.com/aivideoscreated/"
          + fileName + ".mp4"
          + "'>https://storage.googleapis.com/aivideoscreated/"+ fileName + ".mp4</a></h3><br><h4>Thank you for using <a href='https://vikit.ai/#/platform'>Vikit.ai</a> !</h4><br></body></html>"
      )
      sender = {"name": "Vikit.ai", "email": "hello@vikit.ai"}
      to = [{"email": email}]
      
      send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
          to=to, html_content=html_content, sender=sender, subject=subject
      )
  
      try:
          api_response = api_instance.send_transac_email(send_smtp_email)
          print(api_response)
      except ApiException as e:
          print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
    
      print(video_build_settings)
      return "https://storage.googleapis.com/aivideoscreated/" + fileName + ".mp4"
    except  Exception as e:
      firestoreEntry["state"] = "Error: " + str(e)  
      db.collection("apiGenerations").document(generation_id).set(firestoreEntry)
      return "Problem with generation: " + str(e)

