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

Run your computer agent with a goal:

```shell
pdm run start "search for cat images with google"
```

## Roadmap

- [x] Simple implementation of screenshot understanding and computer tool use.
- [ ] Improve structure of actions e.g. with JSON mode.
- [ ] Checkout tool use as in Gemini SDK [Docs](https://ai.google.dev/gemini-api/docs/models/gemini-v2#improved-tools).
- [ ] Improve prompt to prevent some unwanted behaviours.
- [ ] Explore different grounding info formats (2d box vs point, order of coordinates, scaling).
- [ ] Make the agent decide when it's done with the task.
- [ ] Explore Multimodal Live API for screen input [Docs](https://ai.google.dev/gemini-api/docs/models/gemini-v2#live-api)

**Note:** Feel free to open an issue to discuss improvements.