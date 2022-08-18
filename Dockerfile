FROM aiidalab/aiidalab-docker-stack:latest

RUN apt-get update && apt-get install -y git openssh-client && rm -rf /var/lib/apt/lists/*

# Download and install AiiDA plugin for MarketPlace UC3
RUN git config --global user.name "MarketPlace" && git config --global user.email "noreply@materials-marketplace.eu"
RUN mkdir -p /marketplace
RUN --mount=type=secret,id=mp_gitlab_token git clone "https://token:$(cat /run/secrets/mp_gitlab_token)@gitlab.cc-asp.fraunhofer.de/Daniel.Marchand/aiida-marketusercase3.git" /marketplace/aiida-marketusercase3
RUN pip install -e /marketplace/aiida-marketusercase3 && reentry scan

# Copy in UC3 App
COPY *.py *.ipynb LICENSE *.md *.txt *.cfg ${AIIDALAB_APPS}/aiidalab-mp-uc3/
COPY img ${AIIDALAB_APPS}/aiidalab-mp-uc3/img

RUN aiidalab install --yes aiidalab-widgets-base
