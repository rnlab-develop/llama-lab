FROM python:3.10-slim

ARG USERNAME=juja
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create new user 
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -d /userhome \
    # Adding sudo support. 
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

WORKDIR /app
COPY . /app/

RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
