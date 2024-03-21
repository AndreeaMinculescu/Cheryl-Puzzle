# Cheryl's Puzzle Experiment Interface

The code was written in Python 3.10.0 and the package versions are stored in ``requirements.txt``. 
The code can be run by calling ``quickstart.py``. 

* ``all_results`` - the results of the experiment divided by the date the experiment took place.
* ``analysys.py`` - code used to generate the plots in ``plots``
* ``analysys_stat.Rmd`` - R script to conduct the statistical analysis. Using RStudio to open the file is strongly recommended.
* ``analysys_stat.html`` - HTML rendition of the code and results in ``analysis_stat.Rmd``. Opening this file is recommended if the user is not interested in modifying the code.
* ``quickstart.py`` - file to run
* ``puzzle.py`` - main logic for the puzzle: display, formatting, time-keeping, storing participants actions
* ``practice_trials.py`` - main logic for practice trials and detailed puzzle instructions to be shown at the start of the experiment
* ``background_form.py`` - main logic for the background form to be shown at the end of the experiment
* ``window.py`` - general specifications for window formatting (size, color etc)
* ``utilities.py`` - contains useful functions, not necessarily part of the basic work flow 


## Directory tree
```bash
│
├── all_results\
│   │
│   ├── results_0103\
│   │   ├── All answers_*.csv
│   │   ├── Contact info_*.csv
│   │   └── Puzzle Answers_*.csv
│   │
│   ├── results_0502\
│   │   ├── All answers_*.csv
│   │   ├── Contact info_*.csv
│   │   └── Puzzle Answers_*.csv
│   │
│   ├── results_0503\
│   │   ├── All answers_*.csv
│   │   ├── Contact info_*.csv
│   │   └── Puzzle Answers_*.csv
│   │
│   ├── results_0802\
│   │   ├── All answers_*.csv
│   │   ├── Contact info_*.csv
│   │   └── Puzzle Answers_*.csv
│   │
│   ├── results_0902\
│   │   ├── All answers_*.csv
│   │   ├── Contact info_*.csv
│   │   └── Puzzle Answers_*.csv
│   │
│   ├── results_1202\
│   │   ├── All answers_*.csv
│   │   ├── Contact info_*.csv
│   │   └── Puzzle Answers_*.csv
│   │
│   ├── results_1302\
│   │   ├── All answers_*.csv
│   │   ├── Contact info_*.csv
│   │   └── Puzzle Answers_*.csv
│   │
│   ├── results_1402\
│   │   ├── All answers_*.csv
│   │   ├── Contact info_*.csv
│   │   └── Puzzle Answers_*.csv
│   │
│   ├── results_1602\
│   │   ├── All answers_*.csv
│   │   ├── Contact info_*.csv
│   │   └── Puzzle Answers_*.csv
│   │
│   ├── results_1902\
│   │   ├── All answers_*.csv
│   │   ├── Contact info_*.csv
│   │   └── Puzzle Answers_*.csv
│   │
│   ├── results_2102\
│   │   ├── All answers_*.csv
│   │   ├── Contact info_*.csv
│   │   └── Puzzle Answers_*.csv
│   │
│   └── results_2902\
│       ├── All answers_*.csv
│       ├── Contact info_*.csv
│       └── Puzzle Answers_*.csv
│
│
├── img\
│   ├── birthday.png
│   ├── drink.png
│   ├── hair.png
│   ├── sources.txt
│   ├── toy.png
│   └── warning.png
│
├── plots\
│   ├── distrib_acc_participants.png
│   ├── distrib_answers_puzzle.png
│   ├── form_data.txt
│   ├── p-beauty_distrib.png
│   ├── scenario_level_log_time_distrib.png
│   ├── scenario_log_time_distrib.png
│   └── tom_log_time_distrib.png
│
├── text\
│   ├── background_form_intro.txt
│   ├── background_form_outro.txt
│   ├── birthday.txt
│   ├── drink.txt
│   ├── hair.txt
│   ├── p-beauty.txt
│   ├── practice_intro.txt
│   ├── practice_outro.txt
│   ├── practice_puzzle.txt
│   └── toy.txt
│
├── All answers_all.csv
├── Participant puzzles.csv
├── README.md
├── analysis.py
├── analysis_stat.Rmd
├── analysis_stat.html
├── background_form.py
├── practice_trials.py
├── puzzle.py
├── question_bank.csv
├── question_bank.txt
├── quickstart.py
├── requirements.txt
├── utilities.py
└── window.py
```