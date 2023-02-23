FROM ubi8/python-39

# If the container is not run on a registered RHEL system then use this for the base container:
#FROM registry.fedoraproject.org/f35/python3

LABEL maintainer="tbrunell@redhat.com"
USER 0

RUN yum -y install --nodocs opencv-core opencv-contrib  &&\
    yum clean all -y

RUN python3 -m pip install --upgrade pip 
WORKDIR /app
RUN mkdir /app/templates/
RUN pip3 install protobuf==3.20.*
RUN pip3 install mediapipe
RUN pip3 install matplotlib
RUN pip3 install flask

EXPOSE 8080

COPY app.py /app
COPY HowsMySalute.py /app
COPY templates/ /app/templates/
COPY graphics/ /app/static/graphics/

CMD ["python3","app.py"]
