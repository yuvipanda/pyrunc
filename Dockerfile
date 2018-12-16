FROM quay.io/pypa/manylinux1_x86_64

# FIXME: Do a hash check here?
RUN curl -L https://dl.google.com/go/go1.10.3.linux-amd64.tar.gz | tar -xzf - -C /usr/local 

# Install Twine
RUN /opt/python/cp36-cp36m/bin/pip install twine

ADD . .

ENV PATH /opt/python/cp36-cp36m/bin/:/usr/local/go/bin:$PATH