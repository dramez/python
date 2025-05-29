# youtube_downloader.py

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import xml.etree.ElementTree # For catching specific parse error
import traceback # For more detailed error logging

def get_youtube_transcript(video_url: str) -> tuple[str | None, str | None]:
    """
    Downloads the transcript for a given YouTube video URL.
    It tries to fetch and parse available transcripts, attempting alternatives if one fails.

    Args:
        video_url (str): The URL of the YouTube video.

    Returns:
        tuple[str | None, str | None]: A tuple containing (transcript_text, video_id).
                                       Returns (None, video_id) or (None, None) on failure.
    """
    video_id = None
    try:
        if "watch?v=" in video_url:
            video_id = video_url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]

        if not video_id:
            print("Error: Invalid YouTube URL format. Cannot extract video ID.")
            return None, None

        print(f"Attempting to list transcripts for video ID: {video_id}...")
        transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)

        # Create a list of transcripts to try, prioritizing manual ones
        transcripts_to_try = []
        manual_transcripts = []
        generated_transcripts = []

        for t in transcript_list_obj:
            if not t.is_generated:
                manual_transcripts.append(t)
            else:
                generated_transcripts.append(t)

        # Add manual transcripts first, then generated ones
        transcripts_to_try.extend(manual_transcripts)
        transcripts_to_try.extend(generated_transcripts)

        if not transcripts_to_try:
            print(f"Error: No transcripts (manual or generated) listed for video ID: {video_id}.")
            # This case should ideally be caught by NoTranscriptFound from list_transcripts,
            # but as a safeguard if list_transcripts returns an empty iterable.
            return None, video_id

        for i, transcript_candidate in enumerate(transcripts_to_try):
            transcript_type = 'manual' if not transcript_candidate.is_generated else 'generated'
            print(f"\nAttempting to fetch transcript {i+1}/{len(transcripts_to_try)}: "
                  f"Language '{transcript_candidate.language_code}', Type '{transcript_type}'...")
            try:
                transcript_data = transcript_candidate.fetch()
                full_transcript = " ".join([item['text'] for item in transcript_data])
                print(f"Successfully fetched and parsed transcript: Lang '{transcript_candidate.language_code}', Type '{transcript_type}'.")
                return full_transcript, video_id
            except xml.etree.ElementTree.ParseError as e_xml:
                print(f"Warning: Failed to parse XML content for transcript "
                      f"(Lang '{transcript_candidate.language_code}', Type '{transcript_type}'). Error: {e_xml}")
                if i < len(transcripts_to_try) - 1:
                    print("Trying next available transcript...")
                else:
                    print("No more transcripts to try.")
            except Exception as e_fetch: # Catch other errors during fetch for this specific transcript
                print(f"Warning: An unexpected error occurred while fetching or processing transcript "
                      f"(Lang '{transcript_candidate.language_code}', Type '{transcript_type}'). Error: {e_fetch}")
                # You could print traceback.format_exc() here for more detail on e_fetch if needed
                if i < len(transcripts_to_try) - 1:
                    print("Trying next available transcript...")
                else:
                    print("No more transcripts to try.")

        # If loop completes, all attempts failed
        print(f"Error: All available transcripts for video ID {video_id} failed to fetch or parse.")
        return None, video_id

    except TranscriptsDisabled:
        print(f"Error: Transcripts are disabled for video ID: {video_id if video_id else 'unknown'}.")
        return None, video_id
    except NoTranscriptFound: # This is raised by list_transcripts() if no transcripts exist at all
        print(f"Error: No transcripts found listed for video ID: {video_id if video_id else 'unknown'}.")
        return None, video_id
    except Exception as e: # Catch-all for other unexpected errors (e.g., network issues before listing)
        video_id_str = video_id if video_id else "unknown (URL parsing failed or error before ID extraction)"
        print(f"An critical unexpected error occurred in get_youtube_transcript for video ID {video_id_str}: {e}")
        print("Full Traceback:")
        print(traceback.format_exc())
        return None, video_id