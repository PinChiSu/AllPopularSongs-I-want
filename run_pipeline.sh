#!/bin/bash

set -e

export DBT_PROFILES_DIR=/my_dbt_project/

echo In Shell Script
echo "SPOTI_CLIENT_ID: ${SPOTI_CLIENT_ID}"
echo "SPOTI_SECRET: ${SPOTI_SECRET}"
echo "SPOTI_KEYWORD: ${SPOTI_KEYWORD}"

# Scrape data using spotipy
python -m get_data --id ${SPOTI_CLIENT_ID} --s ${SPOTI_SECRET} --k ${SPOTI_KEYWORD}
# 
# # Check if my_dbt_project directory already exists
if [ ! -d "my_dbt_project" ]; then
    # If the directory does not exist, create a new dbt project
    dbt init my_dbt_project
fi

# Run dbt pipeline to find the popular songs
cd my_dbt_project
dbt clean
dbt -d run 
echo Complete!
# Add tracks to a new playlist
cd ..
echo Move back to the root
python -m create_playlists --id ${SPOTI_CLIENT_ID} --s ${SPOTI_SECRET}
