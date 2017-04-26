# Revised-CommAI-env Under Development
A standard environment for machine learning and general AI research
 <a href="https://www.patreon.com/bePatron?u=5636094"
 data-patreon-widget-type="become-patron-button">Become a Patron!</a>

#### The Revised-CommAI-env, Pre-Release Ver. 0.1
Copyright (c) 2017, Stephen B. Hope, All rights reserved, see LICENSE.md for details.

The facebookresearch Team began the implementation of the CommAI-env as detailed by Marco Baroni et al. The abstract is
available in /docs/CommAI_PDF_1701.08954.pdf.

After a line-by-line examination of the repository, I determined an overhaul of the CommAI-env is required
from the ground up, rebuilding it in pure Python >=3.5.

### I am seeking contributions in any form.
- You may open a discussion by clicking the issue tab at the top of the page, New Issue.
- Pull Requests are welcome at any time! Before doing any coding, please check in as the code is being updated daily and
may diverge from your work.

- Service access, financial donations, or any form of sponsorship would be very welcome.
- <a href="https://www.patreon.com/bePatron?u=5636094">Become a Patron!</a>

#### Stephen Hope
Ottawa, Canada
stephenbhope@gmail.com
Tel [00] 1-613-594-4727

 CommAI-env, https://arxiv.org/abs/1511.08130 The Github repository, https://github.com/facebookresearch/CommAI-env

### The facebookresearch/CommAI-env development ceased at beta-testing stage, completely untested, and unlinted.

# The Revised-CommAI-env will refactor all source code to pure Python >=3.5, fully tested and linted.

WIP - Repackage CommAI-env for standard deployments via Docker, Snap, and Virtualbox images.

#### On the environment, CommAI: Evaluating the first steps towards a useful general AI
Marco Baroni, Armand Joulin, Allan Jabri, Germàn Kruszewski, Angeliki Lazaridou, Klemen Simonic, Tomas Mikolov

_With machine learning successfully applied to new daunting problems almost every day, general AI starts looking
like an attainable goal. However, most current research focuses instead on important but narrow applications,
such as image classification or machine translation. We believe this to be largely due to the lack of objective
ways to measure progress towards broad machine intelligence. In order to fill this gap, we propose here a set of
concrete desiderata for general AI, together with a platform to test machines on how well they satisfy such
desiderata, while keeping all further complexities to a minimum._

Source: Cornell University Library, https://arxiv.org/abs/1701.08954

#### Rationale for dropping support of Python 2.x

The current EOL for Python 2.7 is 2020, back-porting with future imports to 2.x adds a layer of unnecessary code,
and is the underlying cause of many of the existing issues. Localizing to Python >=3.5 provides a native bytecode
environment for Python.

#### *** START HERE for General AI Challenge Round1 ***

#### Preparation steps

1. Register for the General AI Challenge at https://www.general-ai-challenge.org/active-rounds

ONHOLD 2. Send an email to Tomas Prokop at b-toprok@microsoft.com and attach a copy of your registration confirmation. He is
the point of contact at Microsoft which is provisioning entrants with access to Azure Cloud Services.

3. If you do not have a **free** Github account register here: https://github.com/

4. (Optional) Visit the contest forum at https://discourse.general-ai-challenge.org/ and introduce yourself. It's early
days in the process so there is little activity to date, traffic is starting to pick up, with collaborations and Teams
assembling.

#### Support and refactoring of the General AI Challenge Round 1, has been dropped due to a lack of participants
The General AI Challenge forums currently indicate a single entrant actively working on a submission.
 The author noted they were not using the General AI Challenge environment for development.  The first round of the
 challenge opened February 14, 2017, and closes in August 2017.

_GoodAI_, and _General AI Challenge_ declined my offer to contribute directly.

Please note they have very unusual practice for reporting, check before posting any issues concerning 'code quality'.
https://github.com/general-ai-challenge/Round1/issues/16
