
async function initializeExperiment() {
  LOG_DEBUG('initializeExperiment');
  ENV_STRUCTURE = loadJson("static/images/optimal_brain_points_v2.json");
  //ENV_STRUCTURE = deeploadJson("static/images/optimal_brain_points_V2.json");
  // only on localhost 
  condition = parseInt(prompt("Condition", "0"))
  console.log("CONDITION", condition)
  console.log(ENV_STRUCTURE["(4, 0, 0, 0, 0, 0, 1, 7, 0, 0, 0, 0, 0, 5, 3)"])
  //var i = 0
  //Object.entries(ENV_STRUCTURE).forEach(([key, value]) => {
  //  console.log(key, value);
  //  i = i +1 
  //  if (i > 20) {
      
  // }
 //});

  ///////////
  // Setup //
  ///////////
  // capture info from Prolific



  // This ensures that images appear exactly when we tell them to.
  //jsPsych.pluginAPI.preloadImages(['static/images/stim1.png','static/images/stim2.png','static/images/stim3.png','static/images/stim4.png','static/images/stim6.png','static/images/stim7.png','static/images/white.png' ]);

  // To avoid repeating ourselves,  we create a variable for a piece
  // of html that we use multiple times.
  var anykey = "<div class='lower message'>Press any key to continue.</div>";

  var linebreak = "<br>"
  var max_qr_level = 4

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




  /////////////////
  // Trials //
  /////////////////
  var attention_test = {
    type: "html-keyboard-response",
    choices: ['f', 'j', 'p'],
    stimulus: `<p> <img src='static/images/white.png' width="150" height="150"> ${linebreak} It is important that you stay attentive troughout this experiment. ${linebreak} Please press p to continue. </p>`,
    on_finish: function (data) {
      data.block_type = "AttentionCheck";
      if (jsPsych.pluginAPI.compareKeys(data.key_press, "p")) {
        data.correct = true;
      } else {
        data.correct = false;
      }
    }
  }

  var process_stimuli = function (item) {
    if (item.associated) {

      item.correct_text = `<p class='feedback'>  <span style="color: #209750;font-size: 30px"> Correct! </span> <br> This is a valid pair, pressing f was the right response. <br> `
      item.incorrect_text = `<p class='feedback'> <span style="color: #9a2020;font-size: 30px"> Incorrect </span> <br> This is a valid pair, pressing f would have been the right response. <br> `
      item.correct_response = 'f'
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
      stimulus_id: "base0",
      qr_level: 0,
      index: 0
    },
    {
      stimulus: ['shec', 'rukt'],
      associated: true,
      stimulus_id: "base1",
      qr_level: 0, 
      index: 1
    },
    {
      stimulus: ['fipt', 'dynk'],
      associated: false,
      stimulus_id: "base2",
      qr_level: 0,
      index: 2
    },
    {
      stimulus: ['shev', 'alvs'],
      associated: false,
      stimulus_id: "base3",
      qr_level: 0,
      index: 3
    },
  ];

  baseline_stimuli.forEach(item => process_stimuli(item));

  var similarity_stimuli = [
    {
      stimulus: ['vomp', 'ancs'],
      associated: true,
      stimulus_id: "sim0",
      qr_level: 0,
      index: 0
    },
    {
      stimulus: ['vonp', 'anzs'],
      associated: true,
      stimulus_id: "sim1",
      qr_level: 0,
      index: 1
    },
    {
      stimulus: ['vonp', 'ancs'],
      associated: false,
      stimulus_id: "sim2",
      qr_level: 0,
      index: 2
    },
    {
      stimulus: ['vomp', 'anzs'],
      associated: false,
      stimulus_id: "sim3",
      qr_level: 0,
      index: 3
    },
    {
      stimulus: ['feph', 'gwug'],
      associated: true,
      stimulus_id: "sim4",
      qr_level: 0,
      index: 4
    },
    {
      stimulus: ['fegh', 'grug'],
      associated: true,
      stimulus_id: "sim5",
      qr_level: 0,
      index: 5
    },
    {
      stimulus: ['feph', 'grug'],
      associated: false,
      stimulus_id: "sim6",
      qr_level: 0,
      index: 6
    },
    {
      stimulus: ['fegh', 'gwug'],
      associated: false,
      stimulus_id: "sim7",
      qr_level: 0,
      index: 7
    },


  ];
  similarity_stimuli.forEach(item => process_stimuli(item));


  var medium_similarity_stimuli = [
    {
      stimulus: ['zonz', 'nylk'],
      associated: true,
      stimulus_id: "medsim0",
      qr_level: 0,
      index: 0
    },
    {
      stimulus: ['zamz', 'nirk'],
      associated: true,
      stimulus_id: "medsim1",
      qr_level: 0,
      index: 1
    },
    {
      stimulus: ['zonz', 'nirk'],
      associated: false,
      stimulus_id: "medsim2",
      qr_level: 0,
      index: 2
    },
    {
      stimulus: ['zamz', 'nylk'],
      associated: false,
      stimulus_id: "medsim3",
      qr_level: 0,
      index: 3
    },
    {
      stimulus: ['murt', 'cwob'],
      associated: true,
      stimulus_id: "medsim4",
      qr_level: 0,
      index: 4
    },
    {
      stimulus: ['mokt', 'cvab'],
      associated: true,
      stimulus_id: "medsim5",
      qr_level: 0,
      index: 5
    },
    {
      stimulus: ['murt', 'cvab'],
      associated: false,
      stimulus_id: "medsim6",
      qr_level: 0,
      index: 6
    },
    {
      stimulus: ['mokt', 'cwob'],
      associated: false,
      stimulus_id: "medsim7",
      qr_level: 0,
      index: 7
    },

  ];

  medium_similarity_stimuli.forEach(item => process_stimuli(item));

  var game_a_cost = 4;
  var game_b_cost = 4;
  var game_c_cost = 4;
  var current_stimuli_selection = similarity_stimuli;

  var select_stimuli = function(stimuli, number){
    tmp = stimuli.sort((a, b) => (a.qr_level < b.qr_level) ? 1 : -1)
    selected_stimuli = tmp.slice(0,number)
    return selected_stimuli
    
  }
  /* defining baseline timeline */
  var baseline_trials = {
    timeline: [{
      type: 'categorize-html',
      stimulus: jsPsych.timelineVariable('stimulus'),
      on_start: function (trial) {
        trial.stimulus = jsPsych.randomization.shuffle(trial.stimulus);
        trial.stimulus = `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${trial.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${trial.stimulus[1]} </p>
          ${linebreak}`
      },
      choices: ['f', 'j'],
      stim_id: jsPsych.timelineVariable('stimulus_id'),
      associated_pair: jsPsych.timelineVariable('associated'),
      qr_level: jsPsych.timelineVariable('qr_level'),
      index : jsPsych.timelineVariable('index'),
      key_answer: jsPsych.timelineVariable('correct_response'),
      correct_text: jsPsych.timelineVariable('correct_text'),
      incorrect_text: jsPsych.timelineVariable('incorrect_text'),
      force_correct_button_press: false,
      show_feedback_on_timeout: false,
      trial_duration: 3500,
      feedback_duration: 2000,
      post_trial_gap: 300,
      prompt: `<p style = "text-align:center;"> Valid pair: press f  ${linebreak} Invalid pair: press j</p>`,
      on_finish: function (data) {
        data.block_type = "Baseline";
        data.associated_pair = this.associated_pair;
        data.stimulus_id = this.stim_id;
        
        data.qr_before = this.qr_level
         
        if (data.correct) {
          ingame_score += 1
          if (this.qr_level < max_qr_level){ 
            baseline_stimuli[this.index].qr_level += 1
          }
        } else {
          if (this.qr_level > 1 && this.qr_level < max_qr_level){ 
          baseline_stimuli[this.index].qr_level -= 1
          }
        }
        if (this.qr_level == 0){
          baseline_stimuli[this.index].qr_level = 1
        }
        data.qr_after = baseline_stimuli[this.index].qr_level
        data.ingame_score = ingame_score
      }
    }],

    timeline_variables: select_stimuli(baseline_stimuli, game_a_cost),
    randomize_order: true
  };

  var medium_similarity_trials = {
    timeline: [{
      type: 'categorize-html',
      stimulus: jsPsych.timelineVariable('stimulus'),
      on_start: function (trial) {
        trial.stimulus = jsPsych.randomization.shuffle(trial.stimulus);
        trial.stimulus = `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${trial.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${trial.stimulus[1]} </p>
          ${linebreak}`
      },
      choices: ['f', 'j'],
      stim_id: jsPsych.timelineVariable('stimulus_id'),
      associated_pair: jsPsych.timelineVariable('associated'),
      qr_level: jsPsych.timelineVariable('qr_level'),
      index : jsPsych.timelineVariable('index'),
      key_answer: jsPsych.timelineVariable('correct_response'),
      correct_text: jsPsych.timelineVariable('correct_text'),
      incorrect_text: jsPsych.timelineVariable('incorrect_text'),
      force_correct_button_press: false,
      show_feedback_on_timeout: false,
      trial_duration: 3500,
      feedback_duration: 2000,
      post_trial_gap: 300,
      prompt: `<p style = "text-align:center;"> Valid pair: press f  ${linebreak} Invalid pair: press j</p>`,
      on_finish: function (data) {
        data.block_type = "MediumSimilarity";
        data.associated_pair = this.associated_pair;
        data.stimulus_id = this.stim_id;
        
        data.qr_before = this.qr_level
        
        if (data.correct) {
          ingame_score += 1
          if (this.qr_level < max_qr_level){ 
            medium_similarity_stimuli[this.index].qr_level += 1
          }
        } else {
          if (this.qr_level > 1 && this.qr_level < max_qr_level){ 
            medium_similarity_stimuli[this.index].qr_level -= 1
          }
        }
        if (this.qr_level == 0){
          medium_similarity_stimuli[this.index].qr_level = 1
        }
        data.qr_after = medium_similarity_stimuli[this.index].qr_level
        data.ingame_score = ingame_score
      }
    }],

    timeline_variables: select_stimuli(medium_similarity_stimuli, game_b_cost),
    randomize_order: true
  };

  

  var update =  function () {console.log("tu", current_stimuli_selection); return current_stimuli_selection};

  /* var similarity_trials = {

    
      type: 'categorize-html',
      stimulus: jsPsych.timelineVariable('stimulus'),
      on_start: function (trial) {
        console.log("tt", current_stimuli_selection);
        trial.stimulus = jsPsych.randomization.shuffle(trial.stimulus);
        trial.stimulus = `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${trial.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${trial.stimulus[1]} </p>
          ${linebreak}`
      },
      choices: ['f', 'j'],
      stim_id: jsPsych.timelineVariable('stimulus_id'),
      associated_pair: jsPsych.timelineVariable('associated'),
      qr_level: jsPsych.timelineVariable('qr_level'),
      index : jsPsych.timelineVariable('index'),
      key_answer: jsPsych.timelineVariable('correct_response'),
      correct_text: jsPsych.timelineVariable('correct_text'),
      incorrect_text: jsPsych.timelineVariable('incorrect_text'),
      force_correct_button_press: false,
      show_feedback_on_timeout: false,
      trial_duration: 3500,
      feedback_duration: 2000,
      post_trial_gap: 300,
      prompt: `<p style = "text-align:center;"> Valid pair: press f  ${linebreak} Invalid pair: press j</p>`,
      on_finish: function (data) {
        data.block_type = "Similarity";
        data.associated_pair = this.associated_pair;
        data.stimulus_id = this.stim_id;
        
        data.qr_before = this.qr_level
        
        if (data.correct) {
          ingame_score += 1
          if (this.qr_level < max_qr_level){ 
            similarity_stimuli[this.index].qr_level += 1
          }
        } else {
          if (this.qr_level > 1 && this.qr_level < max_qr_level){ 
            similarity_stimuli[this.index].qr_level -= 1
          }
        }
        if (this.qr_level == 0){
          similarity_stimuli[this.index].qr_level = 1
        }
        data.qr_after = similarity_stimuli[this.index].qr_level
        data.ingame_score = ingame_score
      }
    };
    
   */
    var trial_stimuli = similarity_stimuli.slice(0,3)
    var similarity_trials = {
      
      timeline: [{
        type: 'categorize-html',
        stimulus: jsPsych.timelineVariable('stimulus'),
        on_start: function (trial) {
          trial.stimulus = jsPsych.randomization.shuffle(trial.stimulus);
          trial.stimulus = `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${trial.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${trial.stimulus[1]} </p>
            ${linebreak}`
        },
        choices: ['f', 'j'],
        stim_id: jsPsych.timelineVariable('stimulus_id'),
        associated_pair: jsPsych.timelineVariable('associated'),
        qr_level: jsPsych.timelineVariable('qr_level'),
        index : jsPsych.timelineVariable('index'),
        key_answer: jsPsych.timelineVariable('correct_response'),
        correct_text: jsPsych.timelineVariable('correct_text'),
        incorrect_text: jsPsych.timelineVariable('incorrect_text'),
        force_correct_button_press: false,
        show_feedback_on_timeout: false,
        trial_duration: 3500,
        feedback_duration: 2000,
        post_trial_gap: 300,
        prompt: `<p style = "text-align:center;"> Valid pair: press f  ${linebreak} Invalid pair: press j</p>`,
        on_finish: function (data) {
          data.block_type = "Similarity";
          data.associated_pair = this.associated_pair;
          data.stimulus_id = this.stim_id;
          
          data.qr_before = this.qr_level
          
          if (data.correct) {
            ingame_score += 1
            if (this.qr_level < max_qr_level){ 
              similarity_stimuli[this.index].qr_level += 1
            }
          } else {
            if (this.qr_level > 1 && this.qr_level < max_qr_level){ 
              similarity_stimuli[this.index].qr_level -= 1
            }
          }
          if (this.qr_level == 0){
            similarity_stimuli[this.index].qr_level = 1
          }
          data.qr_after = similarity_stimuli[this.index].qr_level
          data.ingame_score = ingame_score
          console.log(similarity_stimuli)
          similarity_stimuli.sort((a, b) => (a.qr_level > b.qr_level) ? 1 : -1)
          console.log(similarity_stimuli)

        }
      }],
      //on_timeline_start: function() {
       // alert("hey")
        //trial_stimuli = similarity_stimuli.filter((obj) => obj.qr_level == 0);
      //},
      timeline_variables:  similarity_stimuli,
      sample: {
        type: 'custom',
        fn: function(t){
            return t.slice(0,4); // show the trials in the reverse order
        }},
      //on_timeline_start: function(timeline) {
      //  alert("hi")
       // return timeline.timeline_variables.filter((obj) => obj.qr_level == 0)
      //},
      
        
      randomize_order: false
    };
  
  


  var current_game_choice;
  var ingame_score = 0;
  var overall_score = 0;
  var time_budget = 40;
  


  var game_choice = {
    type: "html-button-response",
    stimulus: `<p>Which game do you want to play? </p>${linebreak}`,
    choices: [`<p style = "font-size: 20px; font-weight: bold">Game A</p> `,
    `<p style = "font-size: 20px; font-weight: bold">Game B</p> `,
    `<p style = "font-size: 20px; font-weight: bold">Game C</p>`],
    //prompt: `${linebreak} Remaining learning budget: ${time_budget}`,
    on_start: function (trial) {
      trial.prompt = `${linebreak} Remaining Choices: ${time_budget} ${linebreak} Your overall score is ${overall_score} points.`
      console.log("tc", current_stimuli_selection)
    },
    on_finish: function (data) {
      current_game_choice = data.button_pressed
      current_stimuli_selection = select_stimuli(similarity_stimuli, game_c_cost)
      data.time = time_budget
      ingame_score = 0
    }
  }

  var game_end_screen = {
    type: "html-keyboard-response",
    stimulus: `Game complete! <br> You scored ${ingame_score} Points! `,
    on_start: function (trial) {
      //trial.stimulus = jsPsych.randomization.shuffle(trial.stimulus);
      overall_score = overall_score + ingame_score
      trial.stimulus = `Game complete! ${linebreak} You scored ${ingame_score} Points. ${linebreak} Your overall score is ${overall_score} points.`
    },
    trial_duration: 3500
  }


  // Random assignement of difficulty level to the three games:
  var conditions = jsPsych.randomization.shuffle([baseline_trials, medium_similarity_trials, similarity_trials])
  console.log("MATCHING", conditions)
  var condition_game_matching = {
    game_a: conditions[0],
    game_b: conditions[1],
    game_c: conditions[2]
  }
  
   



  var game_a = {

    timeline: [condition_game_matching.game_a, game_end_screen],
    conditional_function: function () {
      // get the data from the previous trial,
      // and check which key was pressed

      console.log("CHOICE", current_game_choice);
      if (current_game_choice == 0) {
        time_budget = time_budget - 1
        return true
      } else {
        return false
      }

    },
    
  }

  var game_b = {

    timeline: [condition_game_matching.game_b, game_end_screen],
    conditional_function: function () {
      // get the data from the previous trial,
      // and check which key was pressed

      console.log("CHOICE", current_game_choice);
      if (current_game_choice == 1) {
        time_budget = time_budget - 1
        return true
      } else {
        return false
      }

    }
  }

 var game_c = {

    timeline: [condition_game_matching.game_c, game_end_screen],
    conditional_function: function () {
      // get the data from the previous trial,
      // and check which key was pressed

      console.log("CHOICE", current_game_choice);
      if (current_game_choice == 2) {
        time_budget = time_budget - 1
        return true
      } else {
        return false
      }

      
    },
    on_timeline_start: function() {
      console.log("HIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIHFDGDGDH")},
  }
  /*
  var vars_for_c  = select_stimuli(similarity_stimuli, 3);
  var game_c = {
    
    timeline: [{ 
      timeline: [condition_game_matching.game_c],  
      timeline_variables : vars_for_c,
      on_timeline_start: function() {
        console.log('The trial procedure just started.' )
      },
      randomize_order: true
      
    },
     game_end_screen],
    
    conditional_function: function () {
      // get the data from the previous trial,
      // and check which key was pressed

      console.log("CHOICE", current_game_choice);
      console.log("tg", current_stimuli_selection)
      if (current_game_choice == 2) {
        time_budget = time_budget - 1
        vars_for_c = select_stimuli(similarity_stimuli, 3)
        return true
      } else {
        return false
      }
    }, 
    } 
    */
    
    

    
    

    
    
    
  

  var game = {
    timeline: [game_a, game_b, game_c]
  }



  /////////////////////////
  // Experiment timeline //
  /////////////////////////
  var main_block =  
  {timeline: [game_choice, game],
  repetitions: time_budget}
  
 
  
  

  var timeline = [
    main_block
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


