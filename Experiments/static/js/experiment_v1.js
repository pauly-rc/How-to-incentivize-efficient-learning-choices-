
async function initializeExperiment() {
  LOG_DEBUG('initializeExperiment');
  

  // only on localhost 
  //condition = parseInt(prompt("Condition", "0"))
  console.log("CONDITION", condition)

  ///////////
  // Setup //
  ///////////
  // capture info from Prolific
  var subject_id = jsPsych.data.getURLVariable('PROLIFIC_PID');
  var study_id = jsPsych.data.getURLVariable('STUDY_ID');
  var session_id = jsPsych.data.getURLVariable('SESSION_ID');

  jsPsych.data.addProperties({
    subject_id: subject_id,
    study_id: study_id,
    session_id: session_id
  });

  // trials = await $.getJSON 'static/json/rewards/increasing.json'
 
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
      <p align="left"> You will encounter each pair 5 times. </p>
      <p align = "left"> The first time you see each pair, you will have to guess whether it is valid or not. 
      With time you should be able to use the knowledge you gain from the feedback after each trial to choose more reasonably. </p>
      <p align="left"> The more correct answers you give, the more bonus payment you earn. </p> 
      
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
    <p align="left"> You will now be presented with a list of 6 pairs.
    Each pair will be shown 5 times. </p>
    <p align="left"> The pairs in this list look like this: </p>
    <p style = "font-size: 30px; font-weight: bold;"> urbe <img src='static/images/white.png' width="150" height="150"> tarb </p>
    <p align="left"> Press any key to start with the list. </p>
    `)
  };

  var visual_instruction_block = {
    type: "html-keyboard-response",
    stimulus: markdown(`
    <p align="left"> You will now be presented with a list of 6 pairs.
    Each pair will be shown 5 times. </p>
    <p align="left"> The pairs in this list look like this: </p>
    <p style = "font-size: 30px; font-weight: bold;">  <img src='static/images/stim1.png' width="150" height="150"> <img src='static/images/white.png' width="150" height="150"> tarb </p>
    <p align="left"> Press any key to start with the list. </p>
    `)

  };
  
  var setsize_instruction_block = {
    type: "html-keyboard-response",
    stimulus: markdown(`
    <p align="left"> You will now be presented with a list of 10 pairs.
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
  
  // List of stimuli annotated with whether they represent an associated pair or not 
  var baseline_stimuli = [
    {
    stimulus: ['dwor', 'zuik'],
    associated: true,
    stimulus_id: "base0"
  },
  {
    stimulus: ['prus', 'ceaf'],
    associated: true,
    stimulus_id: "base1"
  },
  {
    stimulus: ['gheg', 'kump'],
    associated: true,
    stimulus_id: "base2"
  },
  {
    stimulus: ['dwor', 'chom'],
    associated: false,
    stimulus_id: "base3"
  },
  {
    stimulus: ['prus', 'pefe'],
    associated: false,
    stimulus_id: "base4"
  },
  {
    stimulus: ['gheg', 'skra'],
    associated: false,
    stimulus_id: "base5"
  }
    
  ];

  var visual_stimuli = [
    {
      stimulus: ['stim2', 'clee'],
      associated: true,
      stimulus_id: "vis0"
    },
    {
      stimulus: ['stim3', 'vafe'],
      associated: true,
      stimulus_id: "vis1"
    },
    {
      stimulus: ['stim4', 'smar'],
      associated: true,
      stimulus_id: "vis2"
    },
    {
      stimulus: ['stim5', 'cilp'],
      associated: false,
      stimulus_id: "vis3"
    },
    {
      stimulus: ['stim6', 'ulch'],
      associated: false,
      stimulus_id: "vis4"
    },
    {
      stimulus: ['stim7', 'grov'],
      associated: false,
      stimulus_id: "vis5"
    }
  ];

  var distractor_stimuli = [
    {
      stimulus: ['clee', 'vafe'],
      associated: true,
      stimulus_id: "dis0"
    },
    {
      stimulus: ['smar', 'cilp'],
      associated: true,
      stimulus_id: "dis1"
    },
    {
      stimulus: ['ulch', 'grov'],
      associated: true,
      stimulus_id: "dis2"
    },
    {
      stimulus: ['clee', 'grov'],
      associated: false,
      stimulus_id: "dis3"
    },
    {
      stimulus: ['smar', 'vafe'],
      associated: false,
      stimulus_id: "dis4"
    },
    {
      stimulus: ['ulch', 'cilp'],
      associated: false,
      stimulus_id: "dis5"
    }
  ];

  var setsize_stimuli = [
    {
      stimulus: ['clee', 'vafe'],
      associated: true,
      stimulus_id: "set0"
    },
    {
      stimulus: ['smar', 'cilp'],
      associated: true,
      stimulus_id: "set1"
    },
    {
      stimulus: ['ulch', 'grov'],
      associated: true,
      stimulus_id: "set2"
    },
    {
      stimulus: ['cauv', 'urbe'],
      associated: true,
      stimulus_id: "set3"
    },
    {
      stimulus: ['fusk', 'tarb'],
      associated: true,
      stimulus_id: "set4"
    },
    {
      stimulus: ['clee', 'demb'],
      associated: false,
      stimulus_id: "set5"
    },
    {
      stimulus: ['smar', 'soys'],
      associated: false,
      stimulus_id: "set6"
    },
    {
      stimulus: ['ulch', 'tovs'],
      associated: false,
      stimulus_id: "set7"
    },
    {
      stimulus: ['cauv', 'gyte'],
      associated: false,
      stimulus_id: "set8"
    },
    {
      stimulus: ['fusk', 'kilv'],
      associated: false,
      stimulus_id: "set9"
    }
  ];

  // Set the key press that's considered correct and the feedback messages based on whether the stimulus pair is associated or not 
  baseline_stimuli.forEach(item => {
     

      item.stimulus = `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${item.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${item.stimulus[1]} </p>
                        ${linebreak}`
      if (item.associated){
      
      item.correct_text = `<p class='feedback'>  <span style="color: #209750"> Correct! </span> <br> This is a valid pair, pressing f was the right response. <br> Press f to continue </p>`
      item.incorrect_text = `<p class='feedback'> <span style="color: #9a2020"> Incorrect </span> <br> This is a valid pair, pressing f would have been the right response. <br> Press f to continue </p>`
      item.correct_response= 'f'
    } else {
      item.correct_text = `<p class='feedback'> <span style="color: #209750"> Correct! </span> <br> This is an invalid pair, pressing j was the right response. <br> Press j to continue </p>`
      item.incorrect_text = `<p class='feedback'> <span style="color: #9a2020"> Incorrect </span> <br> This is an invalid pair, pressing j would have been the right response. <br> Press j to continue </p>`
      item.correct_response = 'j'
    }
  });

  distractor_stimuli.forEach(item => {
     

    item.stimulus = `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${item.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${item.stimulus[1]} </p>
                      ${linebreak}`
    if (item.associated){
    
    item.correct_text = `<p class='feedback'>  <span style="color: #209750"> Correct! </span> <br> This is a valid pair, pressing f was the right response. <br> Press f to continue </p>`
    item.incorrect_text = `<p class='feedback'> <span style="color: #9a2020"> Incorrect </span> <br> This is a valid pair, pressing f would have been the right response. <br> Press f to continue </p>`
    item.correct_response= 'f'
  } else {
    item.correct_text = `<p class='feedback'> <span style="color: #209750"> Correct! </span> <br> This is an invalid pair, pressing j was the right response. <br> Press j to continue </p>`
    item.incorrect_text = `<p class='feedback'> <span style="color: #9a2020"> Incorrect </span> <br> This is an invalid pair, pressing j would have been the right response. <br> Press j to continue </p>`
    item.correct_response = 'j'
  }
});
  setsize_stimuli.forEach(item => {
     

  item.stimulus = `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${item.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${item.stimulus[1]} </p>
                    ${linebreak}`
  if (item.associated){
  
  item.correct_text = `<p class='feedback'>  <span style="color: #209750"> Correct! </span> <br> This is a valid pair, pressing f was the right response. <br> Press f to continue </p>`
  item.incorrect_text = `<p class='feedback'> <span style="color: #9a2020"> Incorrect </span> <br> This is a valid pair, pressing f would have been the right response. <br> Press f to continue </p>`
  item.correct_response= 'f'
} else {
  item.correct_text = `<p class='feedback'> <span style="color: #209750"> Correct! </span> <br> This is an invalid pair, pressing j was the right response. <br> Press j to continue </p>`
  item.incorrect_text = `<p class='feedback'> <span style="color: #9a2020"> Incorrect </span> <br> This is an invalid pair, pressing j would have been the right response. <br> Press j to continue </p>`
  item.correct_response = 'j'
}
});

  visual_stimuli.forEach(item => {
    

      item.stimulus = `<p style = "font-size: 30px; font-weight: bold; text-align:center;"> <img src='static/images/${item.stimulus[0]}.png' width="75" height="150"> <img src='static/images/white.png' width="150" height="350"> ${item.stimulus[1]} </p>
                        ${linebreak}`
      if (item.associated){
      
      item.correct_text = `<p clear:both>  <span style="color: #209750"> Correct! </span> <br> This is a valid pair, pressing f was the right response. <br> Press f to continue </p>`
      item.incorrect_text = `<p clear:both><span style="color: #9a2020"> Incorrect </span> <br> This is a valid pair, pressing f would have been the right response. <br> Press f to continue </p>`
      item.correct_response= 'f'
    } else {
      item.correct_text = `<p clear:both> <span style="color: #209750"> Correct! </span> <br> This is an invalid pair, pressing j was the right response. <br> Press j to continue </p>`
      item.incorrect_text = `<p clear:both><span style="color: #9a2020"> Incorrect </span> <br> This is an invalid pair, pressing j would have been the right response. <br> Press j to continue </p>`
      item.correct_response = 'j'
    }
  });
 

  
    /* defining baseline timeline */
    var baseline_trials = {
      timeline: [{
        type: 'categorize-html',
        choices: ['f', 'j'],
        stimulus: jsPsych.timelineVariable('stimulus'),
        stim_id: jsPsych.timelineVariable('stimulus_id'),
        associated_pair: jsPsych.timelineVariable('associated'),
        key_answer: jsPsych.timelineVariable('correct_response'),
        correct_text: jsPsych.timelineVariable('correct_text'),
        incorrect_text: jsPsych.timelineVariable('incorrect_text'),
        force_correct_button_press: true,
        post_trial_gap: 300,
        prompt: `<p style = "text-align:center;"> Valid pair: press f  ${linebreak} Invalid pair: press j</p>`,
        //data: jsPsych.timelineVariable('data'),
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
  
    var visual_trials = {
      timeline: [{
        type: 'categorize-html',
        choices: ['f', 'j'],
        stimulus: jsPsych.timelineVariable('stimulus'),
        stim_id: jsPsych.timelineVariable('stimulus_id'),
        associated_pair: jsPsych.timelineVariable('associated'),
        key_answer: jsPsych.timelineVariable('correct_response'),
        correct_text: jsPsych.timelineVariable('correct_text'),
        incorrect_text: jsPsych.timelineVariable('incorrect_text'),
        force_correct_button_press: true,
        post_trial_gap: 300,
        prompt: `<p> Valid pair: press f  ${linebreak} Invalid pair: press j</p>` ,
        on_finish: function(data){
          data.block_type= "Visual";
          data.associated_pair = this.associated_pair;
          data.stimulus_id = this.stim_id;
        }
        
        
      }],
      timeline_variables: visual_stimuli,
      randomize_order: true
    };

    var distractor_trials = {
      timeline: [{
        type: 'categorize-html',
        choices: ['f', 'j'],
        stimulus: jsPsych.timelineVariable('stimulus'),
        stim_id: jsPsych.timelineVariable('stimulus_id'),
        associated_pair: jsPsych.timelineVariable('associated'),
        key_answer: jsPsych.timelineVariable('correct_response'),
        correct_text: jsPsych.timelineVariable('correct_text'),
        incorrect_text: jsPsych.timelineVariable('incorrect_text'),
        force_correct_button_press: true,
        post_trial_gap: 300,
        prompt: `<p> Valid pair: press f  ${linebreak} Invalid pair: press j</p>`,
        on_finish: function(data){
          data.block_type= "Distractor";
          data.associated_pair = this.associated_pair;
          data.stimulus_id = this.stim_id;
      }
        
      }],
      timeline_variables: distractor_stimuli,
      randomize_order: true
    };

    var setsize_trials = {
      timeline: [{
        type: 'categorize-html',
        choices: ['f', 'j'],
        stimulus: jsPsych.timelineVariable('stimulus'),
        stim_id: jsPsych.timelineVariable('stimulus_id'),
        associated_pair: jsPsych.timelineVariable('associated'),
        key_answer: jsPsych.timelineVariable('correct_response'),
        correct_text: jsPsych.timelineVariable('correct_text'),
        incorrect_text: jsPsych.timelineVariable('incorrect_text'),
        force_correct_button_press: true,
        post_trial_gap: 300,
        prompt: `<p> Valid pair: press f  ${linebreak} Invalid pair: press j</p>`,
        on_finish: function(data){
          data.block_type= "Setsize";
          data.associated_pair = this.associated_pair;
          data.stimulus_id = this.stim_id;
      }
        
      }],
      timeline_variables: setsize_stimuli,
      randomize_order: true
    };

    if(condition == 0){
      var experimental_block = {
        timeline: [
        visual_instruction_block,        
        {timeline: [visual_trials],
        repetitions: 3},
        attention_test,
        {timeline: [visual_trials],
          repetitions: 2}
        ]
      };
    } else if(condition==1){
      var experimental_block = {
        timeline: [       
        baseline_instruction_block, // is the same as for baseline 
        {timeline: [distractor_trials],
        repetitions: 3},
        attention_test,
        {timeline: [distractor_trials],
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


// tl.push(instruct_loop_po)
//if(PARAMS.feedback){
  // tl.push(training_instruction_po_feedback)
  // tl.push(train_po_binary)

//  tl.push(training_instruction_po_choice)
//  tl.push(train_po_choice)
//}
//else{
//  tl.push(training_instruction_po)
//  tl.push(train_po)
// }
