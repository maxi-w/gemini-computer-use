# Gemini 2.0 Computer Use

## Setup

This project uses PDM to manage Python dependencies. Find installation instructions here: https://pdm-project.org/en/latest/.


### Step 1

Clone the project repository and install dependencies with:

```shell
git clone https://github.com/maxi-w/gemini-computer-use.git
cd gemini-computer-use
pdm install
```

### Step 2

Set an environment variable with your GOOGLE_API_KEY to use Gemini:

```shell
export GOOGLE_API_KEY=YOUR_API_KEY
```

### Step 3

Run your computer agent with:

```shell
pdm run start
```

