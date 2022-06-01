FROM nvidia/cuda:10.2-cudnn8-devel-ubuntu18.04
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata \
    && apt-get install -yy python3.8 python3.8-dev python3.8-venv python3-pip python3-opencv build-essential python3-setuptools libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev \
    && apt clean
RUN pip3 install torch numpy requests timm
COPY . /src
WORKDIR /src
ENTRYPOINT ["python3", "main_test_swinir.py"]
