# Getting Started

## What you are setting up

These skills help Codex turn deal room files and online research into a reusable information layer. The information layer is like a source-linked notebook: each observation is saved with where it came from so it can later support underwriting, questions, summaries, and models.

These initial extraction and research skills do not make conclusions, conduct analysis, or create outputs. They only extract, organize, and preserve underlying evidence.

## 1. Install basic tools

You will need:

- The [Codex app](https://developers.openai.com/codex/app/) installed and signed in.
- Install [Python 3](https://www.python.org/downloads/) using the Windows installer if you do not already have it. The installer normally makes Python available automatically, and Codex will check it during setup.
- A local copy of this repository.

To download the repository without using Git:

1. Open the [Underwriting Skills repository](https://github.com/hyunho308-create/Underwriting-Skills).
2. Select the green **Code** button, then **Download ZIP**.
3. Unzip the downloaded file somewhere permanent, such as your Documents folder.

## 2. Install skills into Codex

After unzipping the repository, open the `Underwriting-Skills` folder as a new project in Codex. Start a chat and paste:

```text
Set up this project for me. Confirm that Python 3 is available, install the Python packages listed in requirements.txt, and install the Hotel Underwriting plugin from this project so I can use its skills in other projects.
```

Allow the requested installation actions. This installs `openpyxl`, the supporting Python package used to read Excel STR reports, and installs the Hotel Underwriting plugin. You only need to complete this setup once on each computer.

If Codex reports an error, ask it to explain the problem in simple terms and finish the setup. Paste any installer error messages into the task when requested.

The plugin should be installed in Codex and your local folder contains all the skills downloaded from GitHub. You can come back to this project later to inspect, modify, delete, or create new skills by prompting Codex directly. For example:

```text
Show me the link to the $extract-management-franchise-data skill.

Update $research-union-status so it returns how many hotels comprising how many keys are union in the city.

Help me create a new skill called $research-fdd-docs that looks up hotel franchise FDDs at https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx and returns...
```

## 3. Set up a deal

Create a new project in Codex and make the data room for the hotel you are underwriting the root folder as a local project. These skills should not change any existing files in the folder. They should write only to the new `.hotel-underwriting` folder created when you run the first skill.

> **Note:** Codex can use a folder on the shared drive as the root of a project, but it was significantly slower than using a local folder and sometimes timed out when working remotely. Having direct access to Morro in the office may speed this up. If you encounter Codex sandbox permission issues or a slow connection through the VPN or Morro, copy the deal folder to your desktop while you work and point the Codex project there instead. You can also work from a copy if you prefer not to give Codex access to a shared-drive folder. Do not point Codex at a SharePoint folder that automatically removes local copies to save space.

Then run these prompts in order in the project:

```text
Use $create-underwriting-folder for this hotel deal room.
```

```text
Use $inventory-deal-room-files for this hotel deal room.
```

```text
Use $categorize-deal-room-files for this hotel deal room.
```

These steps create the project, record the available files, and identify the type of each document. Codex will create a `.hotel-underwriting` folder inside the hotel folder. Leave it in place; it is where these skills will write the hotel's information layer.

## 4. Run the first extraction skill

Choose a source document and ask Codex to use the matching skill. For example:

```text
Use $extract-om-data on the offering memorandum in this project. Build the information layer and show me what was added.
```

Codex should review the source, prepare a reviewable staging file, validate it, and add source-linked observations to the information layer. Other examples include:

```text
Use $extract-str-data on the STR reports in this project.
Use $extract-labor-staffing-data on the available staffing and payroll files.
Use $research-official-site-data for this hotel.
```

See the [catalog](./CATALOG.md) to choose the right skill for a source or research question.

## 5. Review the result

You do not need to open the data files yourself. They are stored as machine-readable JSONL records. Ask Codex:

```text
Summarize the evidence added in this run, identify any conflicts or missing information, and link each point to its source.
```

At a high level, the information layer contains:

- `sources.jsonl`: the files and webpages used.
- `evidence.jsonl`: source-linked observations produced by the skills.
- `derived/`: temporary staging and coverage files that make extraction reviewable.

Repeat the process with additional skills and sources. Each run adds to the same hotel information layer, which can later support underwriting and output skills.

## A few practical rules

- Use one project folder per hotel or deal. For properties that contain multiple years of data rooms or portfolios with multiple properties, point it to one property and one deal room to keep this simple for now.
- Keep original source files in the deal room; the evidence layer points back to them.
- Tell Codex which document to use when multiple similar files exist, although after categorizing the files, Codex should generally know where to look.
- Ask to review uncertain or conflicting findings first instead of forcing Codex to answer.
