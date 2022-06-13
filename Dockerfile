FROM aiidalab/aiidalab-docker-stack:latest

RUN apt-get update && apt-get install -y git openssh-client && rm -rf /var/lib/apt/lists/*

# Download and install AiiDA plugin for MarketPlace UC3
RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan gitlab.cc-asp.fraunhofer.de >> ~/.ssh/known_hosts
RUN git config --global user.name "Casper Welzel Andersen" && git config --global user.email "casper.w.andersen@sintef.no"
RUN mkdir -p /marketplace
RUN --mount=type=ssh git clone --branch aiidav1.6.5 git@gitlab.cc-asp.fraunhofer.de:Daniel.Marchand/aiida-marketusercase3.git /marketplace/aiida-marketusercase3
RUN pip install -e /marketplace/aiida-marketusercase3 && reentry scan

# Copy in UC3 App
COPY *.py *.ipynb LICENSE *.md *.txt *.cfg ${AIIDALAB_APPS}/aiidalab-mp-uc3/
COPY img ${AIIDALAB_APPS}/aiidalab-mp-uc3/img

RUN aiidalab install --yes aiidalab-widgets-base
