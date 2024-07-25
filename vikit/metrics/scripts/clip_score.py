import os
import torch
import cv2
import numpy as np
from PIL import Image
import time
import logging
from tqdm import tqdm
import argparse
import clip


def extract_frames(video_path, frame_rate=10):
    """
    Extract frames from a video at the given frame rate.

    :param video_path: Path to the video file
    :param frame_rate: Number of frames to extract per second
    :return: List of PIL images of extracted frames
    """
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    frames = []
    count = 0

    while success:
        if count % frame_rate == 0:
            # Convert BGR (OpenCV) to RGB (PIL)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            frames.append(pil_image)
        success, image = vidcap.read()
        count += 1

    return frames


def compute_clip_score(video_path, text_prompt, frame_rate=1):
    """
    Compute the CLIP score for a video/prompt pair.

    :param video_path: Path to the video file
    :param text_prompt: The text prompt to compare with video frames
    :param frame_rate: Number of frames to extract per second
    :return: The average CLIP score for the video/prompt pair
    """

    # Check if video exists
    assert os.path.exists(video_path)

    # Extract frames from the video
    frames = extract_frames(video_path, frame_rate)

    # Preprocess the text prompt
    text = clip.tokenize([text_prompt]).to(device)

    # Initialize an empty list to store frame scores
    frame_scores = []

    with torch.no_grad():
        # Calculate the text features
        text_features = model.encode_text(text)

        for frame in frames:
            # Preprocess the frame and move to the same device as the model
            image = preprocess(frame).unsqueeze(0).to(device)

            # Calculate the image features
            image_features = model.encode_image(image)

            # Calculate the cosine similarity between text and image features
            similarity = torch.cosine_similarity(image_features, text_features)
            frame_scores.append(similarity.item())

    # Compute the average score
    avg_score = np.mean(frame_scores)

    return avg_score


# # Example usage
# video_path = "./videos/4.mp4"
# text_prompt = "A woman reading books"
# clip_score = compute_clip_score(video_path, text_prompt, frame_rate=1)
# print(f"CLIP Score: {clip_score}")


def read_text_file(file_path):
    with open(file_path, "r") as f:
        return f.read().strip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir_videos",
        type=str,
        default="./videos",
        help="Specify the path of generated videos",
    )
    parser.add_argument(
        "--dir_prompts",
        type=str,
        default="./prompts",
        help="Specify the path of generated videos",
    )
    parser.add_argument(
        "--metric",
        type=str,
        default="clip_score",
        help="Specify the metric to be used",
    )
    args = parser.parse_args()

    # Load the CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    dir_videos = args.dir_videos
    dir_prompts = args.dir_prompts
    metric = args.metric

    video_paths = [os.path.join(dir_videos, x) for x in os.listdir(dir_videos)]
    prompt_paths = [
        os.path.join(dir_prompts, os.path.splitext(os.path.basename(x))[0] + ".txt")
        for x in video_paths
    ]

    # Create the directory if it doesn't exist
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    os.makedirs("./results", exist_ok=True)
    # Set up logging
    log_file_path = f"./results/{metric}_record.txt"
    # Delete the log file if it exists
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
    # Set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # File handler for writing logs to a file
    file_handler = logging.FileHandler(filename=f"./results/{metric}_record.txt")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(file_handler)
    # Stream handler for displaying logs in the terminal
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(stream_handler)

    # Calculate SD scores for all video-text pairs
    scores = []

    test_num = 10
    test_num = len(video_paths)
    count = 0
    for i in tqdm(range(len(video_paths))):
        video_path = video_paths[i]
        prompt_path = prompt_paths[i]
        if count == test_num:
            break
        else:
            text = read_text_file(prompt_path)
            print(text)
            if metric == "clip_score":
                score = compute_clip_score(video_path, text)
            count += 1
            scores.append(score)
            average_score = sum(scores) / len(scores)
            # count+=1
            logging.info(f"Vid: {os.path.basename(video_path)},  {metric}: {score}")

    # Calculate the average SD score across all video-text pairs
    logging.info(
        f"Final average {metric}: {average_score}, Total videos: {len(scores)}"
    )
