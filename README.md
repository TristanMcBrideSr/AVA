
---

# Ava – (Advanced Voice Assistant) Modular, Multimodal Assistant

## Overview

**Ava** is a modular framework for natural language interaction, real-time voice and keyboard input, dynamic skill execution, and persistent memory per user.

Ava was created using some of Sybil's framework to give inspiration to others.

Some internal structures, patterns, and modules are derived or adapted from Sybil's framework, but have been reworked, stripped, or rewritten for open source clarity and general-purpose use. Proprietary or sensitive logic from Sybil's framework has been removed or replaced with open templates or placeholders. Ava’s public repo contains only code that is freely usable, safe to fork, and meant for learning, adapting, or extending in your own assistant projects.

Ava processes, interprets, and acts on voice or text input using a multi-stage cognitive pipeline and a fully customizable skills system. It provides robust speech synthesis, memory, and animated GUI feedback with total flexibility.

**Highlights:**

* **No vendor lock-in:** Use any API, speech, or NLP backend—no proprietary dependencies.
* **No naming restrictions:** Organize skills, folders, or components however you want.
* **No forced schemas or decorators:** Add skills with plain Python—no required boilerplate.
* **Natural language interface:** Users interact via real speech or text; Ava responds naturally.
* **Flexible skill system:** Add, group, reload, or restrict skills on the fly.
* **Configurable persona and persistent context:** Adjust Ava’s profile, language, etc...

---

## Why Ava?

Traditional voice and AI assistants:

* Enforce rigid schemas, argument requirements, and specific APIs.
* Limit you to specific cloud providers or tool naming.
* Lose all state between runs and make extension complex.

**Ava:**

* Handles voice and text natively with real-time feedback and an animated UI.
* Uses a modular, multi-stage pipeline for input, cognition, and response.
* Remembers user interactions, preferences, and context across sessions.
* Gives you total control over skills, naming, memory, and backend integration.

---

## Key Features

* **Flexible Skill Loading:** Drop in new skills or modules—any name, any folder.
* **Voice & Keyboard Input:** Real-time speech recognition and keyboard fallback.
* **Speech Synthesis:** High-quality, customizable text-to-speech with live GUI output.
* **Cognition Pipeline:** Multi-stage reasoning and skill mapping—adapts to context.
* **Persistent Memory & Profiles:** Stores user and agent attributes, session history, and more.
* **Animated GUI:** Multiple interactive windows, animated feedback, and mode switching.
* **Backend-Agnostic:** Plug in any NLP, vision, or API service—just update your config.
* **System Operations:** Launch applications, back up data, manage states and modes with simple commands.

---

## Configuration
Ava uses a .env file in the root directory for all runtime settings and API keys.

A sample config, .env.temp, is included. Copy or rename .env.temp to .env before running Ava.

Setup steps:

Copy .env.temp to .env, or simply remove .temp from the filename.

Open .env in any text editor.

Fill in your API keys (see file comments for links to get keys).

Example: OPENAI_API_KEY=your-openai-key or GOOGLE_API_KEY=your-google-key

Save the file.

Provider setup:

To switch providers, set PROVIDER to openai or google in .env.

You can set RESPONSE and VISION providers separately; these override the main PROVIDER value.

If you use both, make sure both API keys are set.

Ava loads all settings from .env on startup (using python-dotenv).
Update .env and restart Ava at any time to apply new settings.

Note:
Leaving .env.temp after setup has no effect. Only .env is loaded.

---

## Running Ava Without the IDE
Right-click the AVA.bat file in the root directory and select Create Shortcut.

Right-click the new shortcut, select Properties, then Change Icon, and navigate to the root directory to select AVA.ico.

Move the shortcut to your desktop or any convenient location, and rename it to "Ava".

You can now double-click this shortcut to run Ava without needing the IDE.

---

## Organizing and Naming Your Skills

There are **no required names, and no fixed patterns** in Ava.
You control all naming, grouping, and structure—whatever suits your workflow.

**Examples:**

* Organize by feature, user, or context.
* Place new skills in any one if Ava's skills directories; Ava discovers and loads them automatically.

---

## How It Works

1. **User inputs voice or text:**
   Voice: “Ava, whats the weather.” (Ava is only required for the first input to start the session, subsequent inputs can be just "what's the weather" until you tell Ava to go into standby mode.)
   Keyboard: “What’s the weather?”
2. **Ava processes input:**
   Routes it through voice/keyboard, normalization, and GUI feedback.
3. **Cognition and skill execution:**
   Input passes through a reasoning pipeline and is mapped to available skills—no naming or schema restrictions.
4. **Output and memory:**
   Response is delivered via speech and animated UI, and context is saved for future use.

---

## Example: Comparing Approaches

### 1. With Ava (No Naming or Vendor Lock-In)

* Ava parses, maps, and runs the correct skills—no enforced names or schemas.
* No JSON or TYPED provider constraints required.

---

### 2. Traditional Assistant (Provider Lock-In)

* Define every function and argument in a schema.
* Register everything with a specific API provider.
* Parse and execute only within their naming/structural limits.

> **Ava never requires schemas, naming patterns, or registration—everything is automatic and provider-agnostic.**

---

## Adding and Organizing Skills

* Write skills as plain Python modules—any name and put them in one if Ava's skills directories.
* Reload and manage skills during runtime.
* No registration or boilerplate required.

---

## Why Use Ava?

* **Not locked into any provider.**
* **No forced schemas or decorators.**
* **Flexible skill management:** Name and group skills however you want.
* **Production ready:** Fast, robust, and easy to extend or maintain.

---

## FAQ

**Q: Is some code proprietary?**
A: Yes. Some code is just placeholders or commented out code as it's proprietary code for Sybil's system. But we do give some examples of how you can implement your own code.

**Q: Can I change Ava's name?**
A: Yes. Use any name you like, you can update the .env or just ask Ava to change her name.

**Q: Can I change Ava's gender?**
A: Yes. You can update the .env or you can just ask Ava to change her gender from female to male or male to female.

**Q: Do I need to follow specific names or folder structures for skills?**
A: No. Use any naming or hierarchy you want, just update the Database.py file to match your structure.

**Q: What APIs does Ava support?**
A: Any—OpenAI, Google, or custom. Just update your configuration.

**Q: How does Ava match skills?**
A: Parses natural language and maps to available Python skills—no schema needed.

**Q: Is user memory persistent?**
A: Yes. Ava stores user, and context data across sessions per user.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

Project by:

- Tristan McBride Sr.
- Sybil

