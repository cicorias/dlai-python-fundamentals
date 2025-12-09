# .devcontainer/Dockerfile
FROM rocm/pytorch:rocm7.1_ubuntu24.04_py3.13_pytorch_release_2.9.1

ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=1000

# Ensure the group exists
RUN groupadd --gid $USER_GID $USERNAME || true

# Create the user with the specified UID/GID
RUN useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USERNAME

# Add the user to the 'video' group for ROCm access
RUN usermod -aG video $USERNAME

# Set the user environment in the Docker image
USER $USERNAME