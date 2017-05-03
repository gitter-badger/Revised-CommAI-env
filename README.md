## Revised-CommAI-env Pre-Release Ver. 0.2

#### Setting a new standard for a stable, containerised, development, testing,  and evaluation environment
#### for _Intelligent Machine Learning_ researchers and developers. GNU 3.0+ Licensed

    - Status: Under Development
    - First Beta Testing Release Target: June 2017
    - Vesion 1.0 Release Target: Sept 2017

## Prelude

I began work on the implementation of the CommAI-env based on the release incorporated within the code provided in a
commercial AI contest. After some initial exploration and refactoring, I confirmed my theory it would more efficient
to fork farther upstream. On April 15th I set aside my work to date, and initiated this repository as
a refactor of the Github facebookreseacrh/CommAI-env Beta-Test release.

## WHY NOW?

I was motivated to start publicly coding instead of just contemplating the project privately by: Nat Friedman's
AIGrant: Get $5,000 for your open source AI project:

https://nat.org/aigrant-get-5-000-for-your-open-source-ai-project-1118dd7db083

I am including the initial development from forking as a consequence as part of my entry.

I subscribe to Nat's feed via Medium: https://medium.com Nat is one a number of writers whose work is available
FREE of third party advertising, published at Medium. I make time to read when I see a new post.

## UPDATE May 3, 2017.

### First external expense incurred by the Revised CommAI-env:

Type: Github personal accounts
Purpose: Enable features on top of Github's FREE features

From amount 	$9.91 CAD
To amount 	$7.00 USD
Exchange rate: 1 CAD = 0.706704 USD

May 3, 2017

+ 9.91 CAD
__________

$ 9.91 CAD Total external costs to date.
==========

Nat's contest gained a sponsor, the prize pool has been extended from five $5000 to ten $5000 AI Grants. 

### AI Grant gets a sponsor! Thanks, Floodgate
https://nat.org/ai-grant-gets-a-sponsor-thanks-floodgate-a945afc79470

### Floodgate backs the Prime Movers before the rest of the world believes.
http://floodgate.com/

## Week One Progress Report

I'm very excited at the rapid pace of development as both the Project Lead and as the sole contributor to the
effort. I hit the ground running to speed the process of refactoring my code and docstrings to a level where more than
one contributor can check out files.

### Completed
All Python source files have been refactored into Python style pseudo code, and tagged with notations where
conversions are required to use the code blocks individually as functional code.

The development style here, in regards to the scope of this project, is:

_Any discussion which adds to the progress towards a working implementation of general intelligence must be done in
the form of a logical statement. The form factor does not matter, as an equation, symbolic logic, psuedo code, a
structured language like Python, they all represent the same thing.  Discussions in other media have great value for
other purposes. However for the purposes outlined here are simply not relevant to progress in the implementation of
general AI. Anything outside of those constraints, however well-reasoned, are examples of speculative fiction._

### WIP [Work in Progress]

Creating an Issue for each file containing #TODOs or #FIXME, completion: Week 2.

Everything else. One of the core of elements of my development process is: _Don't spend time preparing for description
of future work when completing the work itself is possible within the given constraints. Also if the task is too
complex to communicate in a few sentences to a peer, it needs to be reduced further._

### METRICS

As the initial week has no baseline to provide metrics, first metrics reports will be provided on May 5, 2017.

### RAW INFORMATION

    - Codeclimate rating from 1.04 - 3.46, 700+ issues, 
      (click Code Climate at top of page for details)
    
    - Excluding merges, I have pushed 365 commits to master and 365 commits to all branches. 
    - On master, 115 files have changed and there have been 14,070 additions and 69 deletions.
    
Raw reports of lines added & deleted, commits, and other activity can be viewed via the Pulse and other tabs at
the top of the page.

### CommAI-env Background

The facebookresearch Team began the implementation of the CommAI-env in summer of 2016. Their work to date has provided
 me with an entry point into the ongoing development of the concepts detailed by Marco Baroni et al. in their paper
 CommAI-env. The abstract is available in /docs/CommAI_PDF_1701.08954.pdf.

### Revsied CommAI-env History

After a line-by-line examination of the facebookresearch implementation, I was inspired by the possibilities a fresh
 perspective could bring to the table, and ultimately contribute to the existing body of work.

The approach I propose to further the development of the source code and documentation are a radical departure from
the conventions I've observed in my limited reviews of existing development work-flows and wfm (workforce management)
strategies.

I am still exploring how best to communicate the work flow information.  A few stubs were added to the Github Wiki here.
https://github.com/stephenbhope/Revised-CommAI-env/wiki

I will be documenting my techniques, tools, and strategies during the process from idea to release 1.0 in the hope
the information will be of use to the community at large to 'cherry pick' any material relevant to their requirements,
work style, and working environment. Or simply as another data point in their set.

### About the LICENSE

The GNU 3.0+ style LICENSE is the most well suited to my objectives. In essence, it grants everyone permission to use
the intellectual property contained in this body (* outside of the actual facebookresearch source code which is
governed by the CommAI-env_software_LICENSE.txt in the root directory). Without charge, forever.

In addition, the GNU license makes this work available without imposing constraints on users or contributors of future
Licensing or Patent enforcement by third parties and opens doors to people bound by other agreements.


### I am seeking contributions in any form.
- You may open a discussion by clicking the issue tab at the top of the page, New Issue.
- Service access, financial donations, or any form of sponsorship would be very welcome.
- <a href="https://www.patreon.com/bePatron?u=5636094">Become a Patron!</a>

#### Stephen Hope
Ottawa, Canada
stephenbhope@gmail.com
Tel [00] 1-613-594-4727

### Join the Revised CommAI-env

By Friday May 5th more structured methods for communicating and sharing will be found in docs/Contributions.md file.


#### On the environment, CommAI: Evaluating the first steps towards a useful general AI
Marco Baroni, Armand Joulin, Allan Jabri, Germàn Kruszewski, Angeliki Lazaridou, Klemen Simonic, Tomas Mikolov

_With machine learning succesfully applied to new daunting problems almost every day, general AI starts looking
like an attainable goal. However, most current research focuses instead on important but narrow applications,
such as image classification or machine translation. We believe this to be largely due to the lack of objective
ways to measure progress towards broad machine intelligence. In order to fill this gap, we propose here a set of
concrete desiderata for general AI, together with a platform to test machines on how well they satisfy such
desiderata, while keeping all further complexities to a minimum._

arXiv:1701.08954v2 [cs.LG]
Cornell University Library, https://arxiv.org/abs/1701.08954

CommAI-env, https://arxiv.org/abs/1511.08130 The Github repository, https://github.com/facebookresearch/CommAI-env

Copyright (c) 2017, Stephen B. Hope, see LICENSE for details.
