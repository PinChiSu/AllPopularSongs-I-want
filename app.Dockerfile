FROM python:3.9.2

# Set the working directory
WORKDIR /

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade spotipy
# Copy the rest of the application code
COPY . .

ARG CLIENT_ID
ARG SECRET
ARG KEYWORD

ENV SPOTI_CLIENT_ID=${CLIENT_ID}
ENV SPOTI_SECRET=${SECRET}
ENV SPOTI_KEYWORD=${KEYWORD}
ENV DBT_PROFILES_DIR=/my_dbt_project

# Set environment variables
RUN echo ${SPOTI_CLIENT_ID}, ${SPOTI_SECRET}, ${SPOTI_KEYWORD}

# Run the application
CMD ["./run_pipeline.sh", "${SPOTI_CLIENT_ID}", "${SPOTI_SECRET}", "${SPOTI_KEYWORD}"]
