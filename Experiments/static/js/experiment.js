

async function initializeExperiment() {
  LOG_DEBUG('initializeExperiment');
  
  
  condition = parseInt(prompt("Condition", "0"))

  console.log("CONDITION", condition)
  // load in the points 
  var ed = document.createElement("w")
  var elemDiv = document.createElement( "loader");
  ed.innerHTML =  `<div id='welcome-message' class='jspsych-content'>
  <h1>Welcome</h1>
  <p>Thanks for accepting our HIT!
  <p>Please wait while we load the experiment.
  <p>Please be patient, loading may take a moment.
</div>`
  elemDiv.innerHTML = "<div id='load-icon'></div>"
  document.body.appendChild(ed);
  document.body.appendChild(elemDiv); 
  if (condition == 0 || condition == 1){
    ENV_STRUCTURE = loadJson("static/images/optimal_brain_points_scaled_1101.json");
  }
  else if (condition == 2 ){
    ENV_STRUCTURE = loadJson("static/images/fc_optimal_points_1101.json");
  } 
  else if (condition == 3 ){
    ENV_STRUCTURE = loadJson("static/images/approx_brain_points_scaled_1027.json");
  } 
  else if (condition == 4){
    ENV_STRUCTURE = loadJson("static/images/fc_approx_points_1101.json");
  }
  
  console.log(ENV_STRUCTURE["400000170000053"]);
  var  point_dict_keys = Object.keys(ENV_STRUCTURE["400000170000053"]);
  document.body.removeChild(elemDiv);
  document.body.removeChild(ed);
  
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

  var basic_instructions_block = {
    type: "html-keyboard-response",
    stimulus: `
      <h2>Instructions</h2>
      <p align="left"> The aim of this experiment is to evaluate how people interact with digital learning environments. For this purpose, we designed a learning environment for learning vocabulary from an artificial language. Your task in this experiment is to learn which word pairs are considered valid in the artificial language and which pairs are considered invalid. 
      </p>     
      <p align="left"> For each pair that is presented to you, you can indicate whether or not you think it is a valid pair. 
      </p>
      <p align="left" style = "font-weight: bold" >If you think it is a valid pair, press f.</p>
      <p align="left" style = "font-weight: bold" >If you think it is an invalid pair, press j.</p>
      <p align="left"> After you make your choice, you will be provided with feedback.  You have 3.5 seconds to respond and the feedback will be shown for 2 seconds. 
      Each pair will be shown several times to give you the opportunity to learn the correct response. </p>
      
      <p align = "left"> The learning environment consists of three different “Games” presenting word pairs. 
      You can choose which of the three you want to play each round.
      There will be 40 rounds overall. Each of the games will allow you to collect points for correct responses. These points make up your overall score. 
      The more correct responses you give, the higher your bonus payment will be. 
      If you master all word pairs before the 40 rounds are completed, you will receive the maximal possible bonus and the experiment will end.
      A word pair is counted as mastered if it is has been answerend correctly often enough. </p>
      
      ${anykey}
      
    `,
    timing_post_trial: 2000
  };

  var points_instructions_block = {
    type: "html-keyboard-response",
    stimulus: `
      <h2>Instructions</h2>
      <p align="left"> The aim of this experiment is to evaluate how people interact with digital learning environments. For this purpose, we designed a learning environment for learning vocabulary from an artificial language. Your task in this experiment is to learn which word pairs are considered valid in the artificial language and which pairs are considered invalid. 
      </p>     
      <p align="left"> For each pair that is presented to you, you can indicate whether or not you think it is a valid pair. 
      </p>
      <p align="left" style = "font-weight: bold" >If you think it is a valid pair, press f.</p>
      <p align="left" style = "font-weight: bold" >If you think it is an invalid pair, press j.</p>
      <p align="left"> After you make your choice, you will be provided with feedback.  You have 3.5 seconds to respond and the feedback will be shown for 2 seconds. 
      Each pair will be shown several times to give you the opportunity to learn the correct response. </p>
      
      <p align = "left"> The learning environment consists of three different “Games” presenting word pairs. 
      You can choose which of the three you want to play each round.
      There will be 40 rounds overall. Each of the games will allow you to collect points for correct responses. These points make up your overall score. 
      The more correct responses you give, the higher your bonus payment will be. 
      If you master all word pairs before the 40 rounds are completed, you will receive the maximal possible bonus and the experiment will end.
      A word pair is counted as mastered if it is has been answerend correctly often enough.
      </p>
      
      <p align = "left"> In order to help you choose which game to play, the learning environment provides you with information on how much each game is expected to help your learning progress. 
      The number of lightbulbs a game is assigned communicate how beneficial playing it is for your learning progress. 
      </p>
      
      
      ${anykey}
      
    `,
    timing_post_trial: 2000
  };

  var forcedchoice_instructions_block = {
    type: "html-keyboard-response",
    stimulus: `
      <h2>Instructions</h2>
      <p align="left"> The aim of this experiment is to evaluate how people interact with digital learning environments. For this purpose, we designed a learning environment for learning vocabulary from an artificial language. Your task in this experiment is to learn which word pairs are considered valid in the artificial language and which pairs are considered invalid. 
      </p>     
      <p align="left"> For each pair that is presented to you, you can indicate whether or not you think it is a valid pair. 
      </p>
      <p align="left" style = "font-weight: bold" >If you think it is a valid pair, press f.</p>
      <p align="left" style = "font-weight: bold" >If you think it is an invalid pair, press j.</p>
      <p align="left"> After you make your choice, you will be provided with feedback.  You have 3.5 seconds to respond and the feedback will be shown for 2 seconds. 
      Each pair will be shown several times to give you the opportunity to learn the correct response. </p>
      
      <p align = "left"> The learning environment consists of three different “Games” presenting word pairs. 
      In each round, the game expected to help you most with your learning progress is chosen for you by the environment.
      It is marked with a lightbulb symbol. 
      There will be 40 rounds overall. Each of the games will allow you to collect points for correct responses. These points make up your overall score. 
      The more correct responses you give, the higher your bonus payment will be.
      If you master all word pairs before the 40 rounds are completed, you will receive the maximal possible bonus and the experiment will end.
      A word pair is counted as mastered if it is has been answerend correctly often enough. </p>
      
      
      
      
      ${anykey}
      
    `,
    timing_post_trial: 2000
  };



  /////////////////
  // Trials //
  /////////////////
  var attention_test = {
    type: "categorize-html",
    choices: ['f', 'j', 'p'],
    stimulus: `<p> <img src='static/images/white.png' width="150" height="150"> ${linebreak} It is important that you stay attentive troughout this experiment. ${linebreak} Please press p to continue. </p>`,
    key_answer: "p",
    feedback_duration: 0,
    on_finish: function (data) {
      data.block_type = "AttentionCheck";
     
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

  var get_stimulus = function() {
    var idx = Math.floor(Math.random() * current_stimuli_selection.length)
    console.log("Get Stimulus: Index ",idx , " selected from ", current_stimuli_selection.length, ". Chosen:  ", current_stimuli_selection[idx] )
    
    stim_index =  current_stimuli_selection.splice(idx, 1)
    return trial_to_game_matching[current_game_choice][stim_index] //  le problem  
  };

  var select_stimuli = function(stimuli, number){
    
    tmp =  []
    Object.assign(tmp, stimuli)
    
    
    tmp.sort((a, b) => (a.qr_level > b.qr_level) ? 1 : -1)

    idx_list = []
    for (let i = 0; i < number; i++){
      idx_list.push(tmp[i].index)
    }
    
    console.log("Selecting Stimuli ", idx_list)
    return idx_list
    
  };

  var check_completion = function(){
    console.log("Checking completion")
    for (let i = 0; i < baseline_stimuli.length; i++){
      if (baseline_stimuli[i].qr_level < 4) {
        console.log("Baseline not completed")
        return false 
      }
    }
    console.log("Baseline completed")
    var m_com = 0 
    var s_com = 0
    for (let i = 0; i < medium_similarity_stimuli.length; i++){
        if (medium_similarity_stimuli[i].qr_level == 4){
            m_com += 1 
        }
        if (similarity_stimuli[i].qr_level == 4){
            s_com += 1 
      }
    }
    if (m_com < 7){
      console.log("Medium Similarity not completed")
      return false
    }
    if (s_com < 7){
      console.log("Similarity not completed")
      return false 
    }
    console.log("Learning completed")
    return true 
  };
  var current_game_choice;
  var ingame_score = 0;
  var scores_per_game = {0:0, 1:0, 2:0}
  var overall_score = 0;
  var time_budget = 40;
  var stimuli_per_game = 4;
  
  var current_stimuli_selection = [];
  var include_attention_check_in_next_game = false;
  var first_loop_activated = false;
  
  var attention_check_idx = 0;
  const attention_check_list =  [33,24,16,6];

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


  var calculate_state = function(){
    // b0, b1, b2, b3, b4 , m0, m1, m2, m3, m4, s0, s1, s2, s3, s4 
    counts = [];
    for (let i = 0; i < stimuli_list.length; i++)  {
      for (let j = 0; j <= max_qr_level; j++) {
        counts.push(String(stimuli_list[i].filter(word => word.qr_level == j).length));
      }
    }
   
    var state =  counts.join(''); 
    return state 
  }

  const stimuli_list = [baseline_stimuli, medium_similarity_stimuli, similarity_stimuli]
  var shuffeled_idx = jsPsych.randomization.shuffle([0,1,2])
  var trial_to_game_matching = [stimuli_list[shuffeled_idx[0]],stimuli_list[shuffeled_idx[1]],stimuli_list[shuffeled_idx[2]]]
  console.log("MATCHING", trial_to_game_matching )
  const point_mapping = []
  
  Object.assign(point_mapping,[point_dict_keys[shuffeled_idx[0]],point_dict_keys[shuffeled_idx[1]],point_dict_keys[shuffeled_idx[2]]])
  console.log("PM", point_mapping)
  
  

  var trials = {
      
      timeline: [{
        type: 'categorize-html',
        
        
        
        stimulus : "default",
        key_answer : "d",
        
        on_start: function (trial) {
          trial.stimulus_dict = get_stimulus(),
          
          trial.stimulus =trial.stimulus_dict.stimulus,
          trial.key_answer = trial.stimulus_dict.correct_response,
          trial.correct_text =  trial.stimulus_dict.correct_text,
          trial.incorrect_text = trial.stimulus_dict.incorrect_text,
          trial.stim_id = trial.stimulus_dict.stimulus_id,
          trial.associated_pair = trial.stimulus_dict.associated,
          trial.qr_level =  trial.stimulus_dict.qr_level,
          trial.index = trial.stimulus_dict.index,

          trial.stimulus = jsPsych.randomization.shuffle(trial.stimulus);
          trial.stimulus = `<p style = "font-size: 30px; font-weight: bold;, text-align:center;"> ${trial.stimulus[0]} <img src='static/images/white.png' width="150" height="350"> ${trial.stimulus[1]} </p>
            ${linebreak}`
        },
        choices: ['f', 'j'],
        
        
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
              trial_to_game_matching[current_game_choice][this.index].qr_level += 1
            }
          } else {
            if (this.qr_level > 1 && this.qr_level < max_qr_level){ 
              trial_to_game_matching[current_game_choice][this.index].qr_level -= 1
            }
          }
          if (this.qr_level == 0){
            trial_to_game_matching[current_game_choice][this.index].qr_level = 1
          }
          data.qr_after = trial_to_game_matching[current_game_choice][this.index].qr_level
          data.ingame_score = ingame_score
          

        }
      }],
    
    };
  
  var log_qr_levels=function(stimuli){
    
    for (let i = 0; i < stimuli.length; i++){
      console.log(stimuli[i].stimulus_id,": ", stimuli[i].qr_level)
    }
  }

  var game_choice = {
    type: "html-button-response",
    stimulus: `<p>Which game do you want to play? </p>${linebreak}`,
    choices: [`<p style = "font-size: 20px; font-weight: bold">Game A</p> `,
    `<p style = "font-size: 20px; font-weight: bold">Game B</p> `,
    `<p style = "font-size: 20px; font-weight: bold">Game C</p>`],
   
    on_start: function (trial) {
      trial.prompt = `${linebreak} Remaining Choices: ${time_budget} ${linebreak} Your overall score is ${overall_score} points.`
      
      //console.log("Here it should come")
      //state = calculate_state()
      //console.log(state)
      var state = calculate_state()
      var point_dict = ENV_STRUCTURE[state]
      var points = [point_dict[point_mapping[0]], point_dict[point_mapping[1]], point_dict[point_mapping[2]]];
      
      if (condition == 1 || condition == 3){
        
        trial.choices= [`<p style = "font-size: 20px; font-weight: bold">Game A</p> <p> <span style="color: #548235;font-weight: bold;font-size: 16px"> ${points[0]}</span><img src='static/images/lightbulb.png' width="25" height="25"> </p> `,
    `<p style = "font-size: 20px; font-weight: bold">Game B</p> <p> <span style="color: #548235;font-weight: bold;font-size: 16px"> ${points[1]}</span><img src='static/images/lightbulb.png' width="25" height="25">  </p> `,
    `<p style = "font-size: 20px; font-weight: bold">Game C</p> <p> <span style="color: #548235;font-weight: bold;font-size: 16px"> ${points[2]}</span><img src='static/images/lightbulb.png' width="25" height="25">  </p> `]
      } else if (condition == 2 || condition == 4){
        var forced_choice = points.indexOf(Math.max(...points));
        trial.choices[forced_choice] =  trial.choices[forced_choice] + ` <p> <img src='static/images/lightbulb.png' width="25" height="25">  </p> `

      }
     
        

     },
    on_load: function(){
      console.log("B")
      log_qr_levels(baseline_stimuli)
      console.log("M")
      log_qr_levels(medium_similarity_stimuli)
      console.log("S")
      log_qr_levels(similarity_stimuli)

      if (condition != 0){
        var state = calculate_state()
        var point_dict = ENV_STRUCTURE[state]
        var points = [point_dict[point_mapping[0]], point_dict[point_mapping[1]], point_dict[point_mapping[2]]];
      }
      if (condition == 2 || condition == 4){
        var forced_choice = points.indexOf(Math.max(...points));
    
        var btns = document.querySelectorAll('.jspsych-html-button-response-button button');
        for(var i=0; i<btns.length; i++){
          if (i != forced_choice){
            btn = document.getElementById("jspsych-html-button-response-button-"+ i)
            btn.id = btn.id + "-deactivated"
            btns[i].setAttribute("disabled", true)
          }
        }
      }
    } ,

    on_finish: function (data) {
      current_game_choice = data.button_pressed
      console.log(time_budget)
      data.time = time_budget
      data.game_choice = data.button_pressed
      state = calculate_state()
      console.log(state)
      data.state = state
      var point_dict = ENV_STRUCTURE[state]
      var points =[point_dict[point_mapping[0]], point_dict[point_mapping[1]], point_dict[point_mapping[2]]];
      data.point_mapping = point_mapping
      console.log(points)
      data.points = points 
      data.forced_choice =  points.indexOf(Math.max(...points));
      console.log(points.indexOf(Math.max(...points)))
      ingame_score = 0
    }
    
    
  }

  var game_end_screen = {
    type: "html-keyboard-response",
    stimulus: `Game complete! <br> You scored ${ingame_score} Points! `,
    choices: "NO_KEYS",
    on_start: function (trial) {
      //trial.stimulus = jsPsych.randomization.shuffle(trial.stimulus);
      overall_score = overall_score + ingame_score
      scores_per_game[current_game_choice] += ingame_score
      console.log(scores_per_game)
      trial.stimulus = `Game complete! ${linebreak} You scored ${ingame_score} Points. ${linebreak} Your overall score is ${overall_score} points.`
      console.log("Game End Screen", overall_score)
      time_budget = time_budget - 1
      if (attention_check_list.includes(time_budget)){
        include_attention_check_in_next_game = true
      } else {
        include_attention_check_in_next_game = false
      }
      if (!first_loop_activated){
        attention_check_idx += 1
        console.log("IDX", attention_check_idx)
      }

    },
    on_finish: function (data){
      data.game_choice = current_game_choice
      data.scoreA = scores_per_game[0]
      data.scoreB = scores_per_game[1]
      data.scoreC = scores_per_game[2]
      data.score = ingame_score
      data.completed = check_completion()
    },
    trial_duration: 3000
  }


  // Random assignement of difficulty level to the three games:
  
  
  
  
  var game_loop = {
    timeline: [trials],
    loop_function: function() {
      if (current_stimuli_selection.length > 0) {
        return true;
      } else {
        return false;
      }
    }
  } 
  

  
  var game_loop_wAttenionCheck = {
    
    timeline: [trials, trials, attention_test, trials, trials],
    
  };

  
  var start_game = {
    
    timeline: [game_loop, game_end_screen], 
    conditional_function: function () {
      
      
      if (include_attention_check_in_next_game){
        first_loop_activated = false
        return false
      
      }
      console.log("First StartGame Loop")
      console.log("CHOICE", current_game_choice, " , ",  trial_to_game_matching[current_game_choice]);
    
      current_stimuli_selection = select_stimuli(trial_to_game_matching[current_game_choice], stimuli_per_game)
      if (current_game_choice == 0) {
        
        console.log("Game A")
        first_loop_activated = true
        return true
      } else if (current_game_choice == 1) {
        console.log("Game B")
        first_loop_activated = true
        return true
      } else if (current_game_choice == 2) {
        console.log("Game C")
        first_loop_activated = true
        return true
      }

    },
    
  };

  var start_game_wAttentioncheck = {
    
    timeline: [game_loop_wAttenionCheck, game_end_screen], 
    conditional_function: function () {
      
      
      if (first_loop_activated){
        return false
      }
      console.log("Second StartGame Loop")
      console.log("CHOICE", current_game_choice, " , ",  trial_to_game_matching[current_game_choice]);
      
      current_stimuli_selection = select_stimuli(trial_to_game_matching[current_game_choice], stimuli_per_game)
      //attention_check_idx += 1
      console.log("IDX", attention_check_idx)
      //console.log(attentioncheck_timelines[attention_check_idx])
      //game_loop_wAttenionCheck.timeline = attentioncheck_timelines[attention_check_idx]
      if (current_game_choice == 0) {
        
        console.log("Game A")
        return true
      } else if (current_game_choice == 1) {
        console.log("Game B")
        return true
      } else if (current_game_choice == 2) {
        console.log("Game C")
        return true
      }

    },
    
  };

  var learning_complete_screen = {
    type: "html-keyboard-response",
    stimulus: `default `,
    on_start: function(trial){
      if (check_completion()){
        console.log("Learning Complete Screen", overall_score)
        trial.stimulus = `Congratulations, you learned very fast and therefore completed the learning task ahead of time! <br> You scored ${overall_score} Points! `
      } else {
        trial.stimulus =  `Congratulations, you completed the learning task! <br> You scored ${overall_score} Points! `
      }
    },
    prompt: "<div class='lower message'>Press any key to end the experiment.</div>"
  };






  /////////////////////////
  // Experiment timeline //
  /////////////////////////
  var main_block =  
  {timeline: [ game_choice, start_game, start_game_wAttentioncheck],
   //repetitions: time_budget,
   loop_function: function() {
   if (time_budget > 0 && !check_completion()){
     return true
   } else {
     return false
   }
  }};
  
 
  
  if (condition == 0){
    var instructions = basic_instructions_block
  } else if (condition == 1){
    var instructions = points_instructions_block
  } else if (condition == 2) {
    var instructions = forcedchoice_instructions_block
  } else if (condition == 3) {
    var instructions = points_instructions_block
  } else if (condition == 4) {
    var instructions = forcedchoice_instructions_block  
  }

  var timeline = [
     instructions, main_block, learning_complete_screen
  ];

  
  


  if (searchParams.get('skip') != null) {
    timeline.splice(0, parseInt(searchParams.get('skip')))
  };


  return startExperiment({
    timeline,
    exclusions: {
      min_width: 800,
      min_height: 400
    },
  });
};


