
async function initializeExperiment() {
  LOG_DEBUG('initializeExperiment');
  

  // only on localhost 
  //condition = parseInt(prompt("Condition", "0"))
  console.log("CONDITION", condition)

  ///////////
  // Setup //
  ///////////
  // capture info from Prolific
  

 
  // This ensures that images appear exactly when we tell them to.
  jsPsych.pluginAPI.preloadImages(['static/images/stim1.png','static/images/stim2.png','static/images/stim3.png','static/images/stim4.png','static/images/stim6.png','static/images/stim7.png','static/images/white.png' ]);

  // To avoid repeating ourselves,  we create a variable for a piece
  // of html that we use multiple times.
  var anykey = "<div class='lower message'>Press any key to continue.</div>";

  var linebreak = "<br>"
  
  //////////////////
  // Instructions //
  //////////////////

  var welcome_block = {
    type: "html-keyboard-response",
    // We use the handy markdown function (defined in utils.js) to format our text.
    stimulus: markdown(`
    # Welcome to the Experiment! 

     

    ${anykey}
    `)
    
  };

  var general_instructions_block = {
    type: "html-keyboard-response",
    stimulus: markdown(`
      <h2>Instructions</h2>
      <p align="left"> The aim of this experiment is to study how people learn vocabulary in a language they don't know.</p>
      <p align="left"> In this experiment you will be presented with pairs of vocabulary from an artificial language. </p>
      <p align="left">Your task is to memorize which of the pairs are considered a valid pair in the artificial language. </p>
      <p align="left">  A valid pair could look like this: </p>
      <p style = "font-size: 30px; font-weight: bold;"> urbe <img src='static/images/white.png' width="150" height="150"> tarb </p>
      <p align="left"> An invalid pair could look like this: </p>
      <p style = "font-size: 30px; font-weight: bold;"> urbe <img src='static/images/white.png' width="150" height="150"> makt </p>
      <br>
      
      <p align="left"> For each pair that is presented to you, you can indicate whether or not you think it is a valid pair. </p>
      <p align="left" style = "font-weight: bold" >If you think it is a valid pair, press f.</p>
      <p align="left" style = "font-weight: bold" >If you think it is an invalid pair, press j.</p>
      <p align="left"> After you make your choice, you will be provided with feedback. </p>
      <p align="left"> You have 3.5 seconds to respond and the feedback will be shown for 2 seconds.</p>
      <p align="left"> You will encounter each pair 5 times. </p>
      <p align = "left"> The first time you see each pair, you will have to guess whether it is valid or not. 
      With time you should be able to use the knowledge you gain from the feedback after each trial to choose more reasonably. </p>
      <p align="left"> The more correct answers you give, the more bonus payment you earn. In order to count towards the bonus, responses have to be given within the time limit.</p> 
      
      <p align="left"> The experiment is divided into two parts. Each part consists of a seperate list of pairs. </p>
      
      <p align="left"> Press any key to start with the first list. </p> 
      <br>
    `),
    timing_post_trial: 2000
  };

  var break_instructions_block = {
    type: "html-keyboard-response",
    stimulus: markdown(`
      <h2>Break</h2>
      <p><img src='static/images/white.png' width="150" height="150"></p>
      <p align="left"> You completed the first part of the experiment. </p> 
      <p align="left"> The second part consists of a new list of pairs. </p> 
      <p align="left"> Press any key to continue to the second list. </p> 
    `),
    timing_post_trial: 2000
  };

  var baseline_instruction_block = {
    type: "html-keyboard-response",
    stimulus: markdown(`
    <p align="left"> You will now be presented with a list of 4 pairs.
    Each pair will be shown 5 times. </p>
    <p align="left"> The pairs in this list look like this: </p>
    <p style = "font-size: 30px; font-weight: bold;"> urbe <img src='static/images/white.png' width="150" height="150"> tarb </p>
    <p align="left"> Press any key to start with the list. </p>
    `)
  };

  var similarity_instruction_block = {
    type: "html-keyboard-response",
    stimulus: markdown(`
    <p align="left"> You will now be presented with a list of 8 pairs.
    Each pair will be shown 5 times. </p>
    <p align="left"> The pairs in this list look like this: </p>
    <p style = "font-size: 30px; font-weight: bold;"> urbe <img src='static/images/white.png' width="150" height="150"> tarb </p>
    <p align="left"> Press any key to start with the list. </p>
    `)
  };

  var double_instruction_block = {
    type: "html-keyboard-response",
    stimulus: markdown(`
    <p align="left"> You will now be presented with a list of 8 pairs, each consisting of two words.
    Each pair will be shown 5 times. </p>
    <p align="left"> The pairs in this list look like this: </p>
    <p style = "font-size: 30px; font-weight: bold;"> urbe zonz <img src='static/images/white.png' width="150" height="150"> tarb cwob </p>
    <p align="left"> Press any key to start with the list. </p>
    `)
  };

    
  var setsize_instruction_block = {
    type: "html-keyboard-response",
    stimulus: markdown(`
    <p align="left"> You will now be presented with a list of 16 pairs.
    Each pair will be shown 5 times. </p>
    <p align="left"> The pairs in this list look like this: </p>
    <p style = "font-size: 30px; font-weight: bold;"> urbe <img src='static/images/white.png' width="150" height="150"> tarb </p>
    <p align="left"> Press any key to start with the list. </p>
    `)

  };


  /////////////////
  // Trials //
  /////////////////
  var attention_test = {
    type: "html-keyboard-response",
    choices: ['f', 'j', 'p'],
    stimulus: `<p> <img src='static/images/white.png' width="150" height="150"> ${linebreak} It is important that you stay attentive troughout this experiment. ${linebreak} Please press p to continue. </p>`,
    on_finish: function(data){
      data.block_type= "AttentionCheck";
      if(jsPsych.pluginAPI.compareKeys(data.key_press, "p")){
        data.correct = true;
      } else {
        data.correct = false; 
      }
  }
  }

  var process_stimuli = function(item){
    if (item.associated){
    
      item.correct_text = `<p class='feedback'>  <span style="color: #209750;font-size: 30px"> Correct! </span> <br> This is a valid pair, pressing f was the right response. <br> `
      item.incorrect_text = `<p class='feedback'> <span style="color: #9a2020;font-size: 30px"> Incorrect </span> <br> This is a valid pair, pressing f would have been the right response. <br> `
      item.correct_response= 'f'
    } else {
      item.correct_text = `<p class='feedback'> <span style="color: #209750;font-size: 30px"> Correct! </span> <br> This is an invalid pair, pressing j was the right response. <br>  </p>`
      item.incorrect_text = `<p class='feedback'> <span style="color: #9a2020;font-size: 30px"> Incorrect </span> <br> This is an invalid pair, pressing j would have been the right response. <br>  </p>`
      item.correct_response = 'j'
    }
    return item
  };
  
  // List of stimuli annotated with whether they represent an associated pair or not 
  var baseline_stimuli = [
    {
    stimulus: ['fipt', 'bonk'],
    associated: true,
    stimulus_id: "base0"
  },
  {
    stimulus: ['shec', 'rukt'],
    associated: true,
    stimulus_id: "base1"
  },
  {
    stimulus: ['fipt', 'dynk'],
    associated: false,
    stimulus_id: "base2"
  },
  {
    stimulus: ['shev', 'alvs'],
    associated: false,
    stimulus_id: "base3"
  },
  ];

  baseline_stimuli.forEach(item => process_stimuli(item));

  var similarity_stimuli = [
    {
      stimulus: ['vomp', 'ancs'],
      associated: true,
      stimulus_id: "sim0"
    },
    {
      stimulus: ['vonp', 'anzs'],
      associated: true,
      stimulus_id: "sim1"
    },
    {
      stimulus: ['vonp', 'ancs'],
      associated: false,
      stimulus_id: "sim2"
    },
    {
      stimulus: ['vomp', 'anzs'],
      associated: false,
      stimulus_id: "sim3"
    },
    {
      stimulus: ['feph', 'gwug'],
      associated: true,
      stimulus_id: "sim4"
    },
    {
      stimulus: ['fegh', 'grug'],
      associated: true,
      stimulus_id: "sim5"
    },
    {
      stimulus: ['feph', 'grug'],
      associated: false,
      stimulus_id: "sim6"
    },
    {
      stimulus: ['fegh', 'gwug'],
      associated: false,
      stimulus_id: "sim7"
    },
    
  
  ];
  similarity_stimuli.forEach(item => process_stimuli(item));
  

  var setsize_stimuli = [
    {
      stimulus: ['zonz', 'nylk'],
      associated: true,
      stimulus_id: "set0"
    },
    {
      stimulus: ['fubb', 'cwob'],
      associated: true,
      stimulus_id: "set1"
    },
    {
      stimulus: ['veav', 'knyz'],
      associated: true,
      stimulus_id: "set2"
    },
    {
      stimulus: ['murt', 'yoes'],
      associated: true,
      stimulus_id: "set3"
    },
    {
      stimulus: ['fost', 'zict'],
      associated: true,
      stimulus_id: "set4"
    },
    {
      stimulus: ['wope', 'filf'],
      associated: true,
      stimulus_id: "set5"
    },
    {
      stimulus: ['nooc', 'twes'],
      associated: true,
      stimulus_id: "set6"
    },
    {
      stimulus: ['nels', 'spyc'],
      associated: true,
      stimulus_id: "set7"
    },
    {
      stimulus: ['zonz', 'zict'],
      associated: false,
      stimulus_id: "set8"
    },
    {
      stimulus: ['fubb', 'filf'],
      associated: false,
      stimulus_id: "set9"
    },
    {
      stimulus: ['veav', 'twes'],
      associated: false,
      stimulus_id: "set10"
    },
    {
      stimulus: ['murt', 'spyc'],
      associated: false,
      stimulus_id: "set11"
    },
    {
      stimulus: ['fost', 'nylk'],
      associated: false,
      stimulus_id: "set12"
    },
    {
      stimulus: ['wope', 'cwop'],
      associated: false,
      stimulus_id: "set13"
    },
    {
      stimulus: ['nooc', 'knyz'],
      associated: false,
      stimulus_id: "set14"
    },
    {
      stimulus: ['nels', 'yoes'],
      associated: false,
      stimulus_id: "set15"
    }
  ];

  setsize_stimuli.forEach(item => process_stimuli(item));

  var double_stimuli = [
    {
    stimulus: ['preg  hilv', 'zubs  qued'],
    associated: true,
    stimulus_id: "double0"
  },
  {
    stimulus: ['preg  qued', 'zubs  hilv'],
    associated: false,
    stimulus_id: "double1"
  },
  {
    stimulus: ['coaz  rert', 'deec  nibe'],
    associated: true,
    stimulus_id: "double2"
  },
  {
    stimulus: ['coaz  nibe', 'deec  rert'],
    associated: false,
    stimulus_id: "double3"
  },
  {
    stimulus: ['fubb  cwop', 'fost  zict'],
    associated: true,
    stimulus_id: "double4"
  },
  {
    stimulus: ['fubb  zict', 'fost  cwop'],
    associated: false,
    stimulus_id: "double5"
  },
  {
    stimulus: ['nyln  klaz ', 'soag  yesc'],
    associated: true,
    stimulus_id: "double6"
  },
  {
    stimulus: ['nyln  yesc', 'soag  klaz'],
    associated: false,
    stimulus_id: "double7"
  },

    
  ];
  double_stimuli.forEach(item => process_stimuli(item));


  
   
    /* defining baseline timeline */
    var baseline_trials = {
      timeline: [{
        type: 'categorize-html',
        stimulus: jsPsych.timelineVariable('stimulus'),
        on_start: function(trial) {
          trial.stimulus = jsPsych.randomization.shuffle(trial.stimulus);
          trial.stimulus =  `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${trial.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${trial.stimulus[1]} </p>
          ${linebreak}` 
        },
        choices: ['f', 'j'],
        stim_id: jsPsych.timelineVariable('stimulus_id'),
        associated_pair: jsPsych.timelineVariable('associated'),
        key_answer: jsPsych.timelineVariable('correct_response'),
        correct_text: jsPsych.timelineVariable('correct_text'),
        incorrect_text: jsPsych.timelineVariable('incorrect_text'),
        force_correct_button_press: false,
        show_feedback_on_timeout: false,
        trial_duration: 3500,
        feedback_duration: 2000,
        post_trial_gap: 300,
        prompt: `<p style = "text-align:center;"> Valid pair: press f  ${linebreak} Invalid pair: press j</p>`,
        on_finish: function(data){
            data.block_type= "Baseline";
            data.associated_pair = this.associated_pair;
            data.stimulus_id = this.stim_id;
        }
      }],

      timeline_variables: baseline_stimuli,
      randomize_order: true
    };


    var baseline_block = {
      timeline: [        
        baseline_instruction_block,
      {timeline: [baseline_trials],
      repetitions: 3},
      attention_test,
      {timeline: [baseline_trials],
        repetitions: 2}
      ]
    };
  
    var setsize_trials = {
      timeline: [{
        type: 'categorize-html',
        stimulus: jsPsych.timelineVariable('stimulus'),
        on_start: function(trial) {
          trial.stimulus = jsPsych.randomization.shuffle(trial.stimulus);
          trial.stimulus =  `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${trial.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${trial.stimulus[1]} </p>
          ${linebreak}` 
        },
        choices: ['f', 'j'],
        stim_id: jsPsych.timelineVariable('stimulus_id'),
        associated_pair: jsPsych.timelineVariable('associated'),
        key_answer: jsPsych.timelineVariable('correct_response'),
        correct_text: jsPsych.timelineVariable('correct_text'),
        incorrect_text: jsPsych.timelineVariable('incorrect_text'),
        force_correct_button_press: false,
        show_feedback_on_timeout: false,
        trial_duration: 3500,
        feedback_duration: 2000,
        post_trial_gap: 300,
        prompt: `<p style = "text-align:center;"> Valid pair: press f  ${linebreak} Invalid pair: press j</p>`,
        on_finish: function(data){
            data.block_type= "Setsize";
            data.associated_pair = this.associated_pair;
            data.stimulus_id = this.stim_id;
        }
      }],

      timeline_variables: setsize_stimuli,
      randomize_order: true
    };

    var double_trials = {
      timeline: [{
        type: 'categorize-html',
        stimulus: jsPsych.timelineVariable('stimulus'),
        on_start: function(trial) {
          trial.stimulus = jsPsych.randomization.shuffle(trial.stimulus);
          trial.stimulus =  `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${trial.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${trial.stimulus[1]} </p>
          ${linebreak}` 
        },
        choices: ['f', 'j'],
        stim_id: jsPsych.timelineVariable('stimulus_id'),
        associated_pair: jsPsych.timelineVariable('associated'),
        key_answer: jsPsych.timelineVariable('correct_response'),
        correct_text: jsPsych.timelineVariable('correct_text'),
        incorrect_text: jsPsych.timelineVariable('incorrect_text'),
        force_correct_button_press: false,
        show_feedback_on_timeout: false,
        trial_duration: 3500,
        feedback_duration: 2000,
        post_trial_gap: 300,
        prompt: `<p style = "text-align:center;"> Valid pair: press f  ${linebreak} Invalid pair: press j</p>`,
        on_finish: function(data){
            data.block_type= "Double";
            data.associated_pair = this.associated_pair;
            data.stimulus_id = this.stim_id;
        }
      }],

      timeline_variables: double_stimuli,
      randomize_order: true
    };



    var similarity_trials = {
      timeline: [{
        type: 'categorize-html',
        stimulus: jsPsych.timelineVariable('stimulus'),
        on_start: function(trial) {
          trial.stimulus = jsPsych.randomization.shuffle(trial.stimulus);
          trial.stimulus =  `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${trial.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${trial.stimulus[1]} </p>
          ${linebreak}` 
        },
        choices: ['f', 'j'],
        stim_id: jsPsych.timelineVariable('stimulus_id'),
        associated_pair: jsPsych.timelineVariable('associated'),
        key_answer: jsPsych.timelineVariable('correct_response'),
        correct_text: jsPsych.timelineVariable('correct_text'),
        incorrect_text: jsPsych.timelineVariable('incorrect_text'),
        force_correct_button_press: false,
        show_feedback_on_timeout: false,
        trial_duration: 3500,
        feedback_duration: 2000,
        post_trial_gap: 300,
        prompt: `<p style = "text-align:center;"> Valid pair: press f  ${linebreak} Invalid pair: press j</p>`,
        on_finish: function(data){
            data.block_type= "Similarity";
            data.associated_pair = this.associated_pair;
            data.stimulus_id = this.stim_id;
        }
      }],

      timeline_variables: similarity_stimuli,
      randomize_order: true
    };

    

    if(condition == 0){
      var experimental_block = {
        timeline: [
        double_instruction_block,        
        {timeline: [double_trials],
        repetitions: 3},
        attention_test,
        {timeline: [double_trials],
          repetitions: 2}
        ]
      };
    } else if(condition==1){
      var experimental_block = {
        timeline: [       
        similarity_instruction_block,
        {timeline: [similarity_trials],
        repetitions: 3},
        attention_test,
        {timeline: [similarity_trials],
          repetitions: 2}
        ]
      };
    } else if(condition==2){
        var experimental_block = {
          timeline: [       
          setsize_instruction_block,  
          {timeline: [setsize_trials],
          repetitions: 3},
          attention_test,
          {timeline: [setsize_trials],
            repetitions: 2}
          ]
        };
      }
      
    
    

    var blocks = jsPsych.randomization.shuffle([baseline_block, experimental_block]);
    
    

  /////////////////////////
  // Experiment timeline //
  /////////////////////////
  
  
  var timeline = [
    //baseline_block
    welcome_block,
    general_instructions_block,
    blocks[0],
    break_instructions_block,
    blocks[1],
    
    
  ];

  
  if (searchParams.get('skip') != null) {
    timeline.splice(0, parseInt(searchParams.get('skip')))
  }


  return startExperiment({
    timeline,
    exclusions: {
      min_width: 800,
      min_height: 400
    },
  });
};


