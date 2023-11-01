#!/usr/bin/env python
import math
import sys
import mysql.connector

from os import name
from pathlib import Path
from subprocess import Popen
from typing import NoReturn

from prawcore import ResponseException
from utils.console import print_substep
from reddit.subreddit import get_subreddit_threads
from utils import settings
from utils.cleanup import cleanup
from utils.console import print_markdown, print_step
from utils.id import id
from utils.version import checkversion
from video_creation.background import (
    download_background_video,
    download_background_audio,
    chop_background,
    get_background_config,
)
from video_creation.final_video import make_final_video
from video_creation.screenshot_downloader import get_screenshots_of_reddit_posts
from video_creation.voices import save_text_to_mp3
from utils.ffmpeg_install import ffmpeg_install
from mysql.connector import connect, Error
from pyutil import filereplace

__VERSION__ = "3.2.1"

print(
    """
██████╗ ███████╗██████╗ ██████╗ ██╗████████╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗     ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗    ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║       ██║   ██║██║██║  ██║█████╗  ██║   ██║    ██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝
██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║       ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║███████╗██████╔╝██████╔╝██║   ██║        ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝    ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚═╝   ╚═╝         ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""
)
# Modified by JasonLovesDoggo
print_markdown(
    "### Thanks for using this tool! Feel free to contribute to this project on GitHub! If you have any questions, feel free to join my Discord server or submit a GitHub issue. You can find solutions to many common problems in the documentation: https://reddit-video-maker-bot.netlify.app/"
)
checkversion(__VERSION__)

def main(POST_ID=None,objfila=None) -> None:
    global redditid, reddit_object
    reddit_object = get_subreddit_threads(POST_ID)
    redditid = id(reddit_object)
    length, number_of_comments = save_text_to_mp3(reddit_object)
    length = math.ceil(length)

    get_screenshots_of_reddit_posts(reddit_object, number_of_comments)
    bg_config = {
        "video": get_background_config("video"),
        "audio": get_background_config("audio"),
    }

    download_background_video(bg_config["video"])
    download_background_audio(bg_config["audio"])
    chop_background(bg_config, length, reddit_object)
    make_final_video(number_of_comments, length, reddit_object, bg_config, objfila)

def run_many(times) -> None:
    for x in range(1, times + 1):
        print_step(
            f'on the {x}{("th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th")[x % 10]} iteration of {times}'
        )  # correct 1st 2nd 3rd 4th 5th....
        main()
        Popen("cls" if name == "nt" else "clear", shell=True).wait()


def shutdown() -> NoReturn:
    if "redditid" in globals():
        print_markdown("## Clearing temp files")
        cleanup(redditid)

    print("Exiting...")
    sys.exit()


if __name__ == "__main__":
    if sys.version_info.major != 3 or sys.version_info.minor != 10:
        print(
            "Hey! Congratulations, you've made it so far (which is pretty rare with no Python 3.10). Unfortunately, this program only works on Python 3.10. Please install Python 3.10 and try again."
        )
        sys.exit()
    ffmpeg_install()
    directory = Path().absolute()
    config = settings.check_toml(
        f"{directory}/utils/.config.template.toml", f"{directory}/config.toml"
    )
    config is False and sys.exit()

    cnx = mysql.connector.connect(host="209.126.104.82", user="negocioi_wp", password="(rf)K4T7VAy6", database="negocioi_wp")  
        
    #Verificamos se tem algum vídeo sendo gerado
    query = "SELECT count(*) as total FROM wp_fila WHERE executado = 1"
    cursor = cnx.cursor()
    cursor.execute(query)
    objExecutando = cursor.fetchone()
    if(objExecutando[0]>0):
        exit("Não vamos executar. Tem vídeo video sendo produzido")

    query = "SELECT * FROM wp_fila WHERE executado = 0 ORDER BY data_execucao LIMIT 0,1"
    cursor = cnx.cursor()
    cursor.execute(query)
    objfila = cursor.fetchone()
    
    if (not objfila):
        exit("Nenhum video em fila para ser executado. Encerrando")

    

    #objfila = []
    #objfila.append('1');
    #objfila.append('2');
    #objfila.append('rocket-league')
    #objfila.append('lofi')
    #objfila.append('Bella')
    #objfila.append('0ac7df1446c8867c18add29505b4afa1')

    settings.config["settings"]["background"]["background_video"] = objfila[2]
    settings.config["settings"]["background"]["background_audio"] = objfila[3]
    settings.config["settings"]["tts"]["elevenlabs_voice_name"] = objfila[4]
    settings.config["settings"]["tts"]["elevenlabs_api_key"] = objfila[5]
    settings.config["reddit"]["creds"]["client_id"] = objfila[6]
    settings.config["reddit"]["creds"]["client_secret"] = objfila[7]
    settings.config["reddit"]["creds"]["username"] = objfila[8]
    settings.config["reddit"]["creds"]["password"] = objfila[9]
    settings.config["reddit"]["thread"]["subreddit"] = objfila[10]
    settings.config["reddit"]["thread"]["min_comments"] = objfila[11]
    settings.config["reddit"]["thread"]["post_lang"] = objfila[12]
    if not objfila[12]:
        settings.config["reddit"]["thread"]["post_lang"]  ="pt"

    # filereplace("config.toml",'client_id = "(.*)"','client_id = "'+str(objfila[6])+'"')
    # filereplace("config.toml",'client_secret = "(.*)"','client_secret = "'+str(objfila[7])+'"')
    # filereplace("config.toml",'username = "(.*)"','username = "'+str(objfila[8])+'"')
    # filereplace("config.toml",'password = "(.*)"','password = "'+str(objfila[9])+'"')
    # filereplace("config.toml",'subreddit = "(.*)"','subreddit = "'+str(objfila[10])+'"')
    # filereplace("config.toml",'min_comments = "(.*)"','min_comments = "'+str(objfila[11])+'"')

    
    if (
        not settings.config["settings"]["tts"]["tiktok_sessionid"]
        or settings.config["settings"]["tts"]["tiktok_sessionid"] == ""
    ) and config["settings"]["tts"]["voice_choice"] == "tiktok":
        print_substep(
            "TikTok voice requires a sessionid! Check our documentation on how to obtain one.",
            "bold red",
        )
        sys.exit()
    
    query = "UPDATE wp_fila SET executado = 1 WHERE id = "+str(objfila[0])
    cursor.execute(query)
    cnx.commit()

    try:
        # if config["reddit"]["thread"]["post_id"]:
        #     for index, post_id in enumerate(config["reddit"]["thread"]["post_id"].split("+")):
        #         index += 1
        #         print_step(
        #             f'on the {index}{("st" if index % 10 == 1 else ("nd" if index % 10 == 2 else ("rd" if index % 10 == 3 else "th")))} post of {len(config["reddit"]["thread"]["post_id"].split("+"))}'
        #         )
        #         main(post_id)
        #         Popen("cls" if name == "nt" else "clear", shell=True).wait()
                
        # elif config["settings"]["times_to_run"]:
        #     run_many(config["settings"]["times_to_run"])
        # else:
            main(None,objfila)
    except KeyboardInterrupt:
        shutdown()
    except ResponseException:
        query = "UPDATE wp_fila SET executado = 4 WHERE id = "+str(objfila[0])
        cursor.execute(query)
        cnx.commit()    
        print_markdown("## Invalid credentials")
        print_markdown("Please check your credentials in the config.toml file")
        shutdown()
    except Exception as err:
        if ("list index out of range" in str(err)):
            query = "UPDATE wp_fila SET executado = 6,erro='"+str(err)+"' WHERE id = "+str(objfila[0])
        elif ("Unusual activity detected" in str(err)):
            query = "UPDATE wp_fila SET executado = 7,erro='"+str(err)+"' WHERE id = "+str(objfila[0])        
        elif ("Unsupported to_language" in str(err)):
            # Vamos tentar novamente
            query = "UPDATE wp_fila SET executado = 0,erro='"+str(err)+"' WHERE id = "+str(objfila[0])        
        elif ("Your reddit credentials are incorrect" in str(err)):
            
            query = "UPDATE wp_fila SET executado = 4,erro='"+str(err)+"' WHERE id = "+str(objfila[0])        
        else:
            query = "UPDATE wp_fila SET executado = 5,erro='"+str(err)+"' WHERE id = "+str(objfila[0])

        cursor.execute(query)
        cnx.commit()    
        config["settings"]["tts"]["tiktok_sessionid"] = "REDACTED"
        config["settings"]["tts"]["elevenlabs_api_key"] = "REDACTED"
        
        print_step(
            f"Sorry, something went wrong with this version! Try again, and feel free to report this issue at GitHub or the Discord community.\n"
            f"Version: {__VERSION__} \n"
            f"Error: {err} \n"
            f'Config: {config["settings"]}'
        )
        raise err
