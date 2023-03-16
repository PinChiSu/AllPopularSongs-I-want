#!/bin/bash

set -e

# Parse command line arguments
while getopts ":i:s:k:" flag; do
    case "${flag}" in
        i) 
            client_id=${OPTARG}
            echo $client_id
            ;;
        s) 
            secret=${OPTARG}
            echo $secret
            ;;
        k)
            keyword=${OPTARG}
            echo $keyword
            ;;
    esac
done

# Scrape data using spotipy
python -m get_data --id $client_id --s $secret --k $keyword

# Run dbt pipeline
if cd my_dbt_project; then
    echo "Move to my_dbt_project"
    dbt init my_dbt_project
    dbt run
else
    echo "invalid path!"
fi

# Add tracks to a new playlist
cd ..
python -m create_playlist --id $client_id --s $secret
