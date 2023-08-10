
   let timers = [];


    // Function to populate the structure_type dropdown
function populateStructureTypeDropdown() {
    const dropdown = $('#structure_type');

    $.ajax({
        url: '/api/structure_type_options',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            const optionsHTML = data.map((option, index) => {
                return `<option value="${option}" data-image-src="image_${index + 1}.jpg">${option}</option>`;
            }).join('');
            dropdown.html(optionsHTML);
        },
        error: function(error) {
            console.error('Error fetching dropdown options:', error);
        }
    });
}

function populateRadioButtons() {
    const radioButtonsContainer = $("#categoryContainer");
    radioButtonsContainer.empty();

    // Fetch radio button options from the server
    $.ajax({
        url: '/api/radio_button_options',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            const options = data;
            options.forEach(option => {
                const radioButton = $("<div>").addClass("form-check");
                radioButton.html(`
                    <input class="form-check-input" type="radio" name="category" value="${option.toLowerCase()}" id="${option.toLowerCase()}">
                    <label class="form-check-label" for="${option.toLowerCase()}">${option}</label>
                `);
                radioButtonsContainer.append(radioButton);
            });
        },
        error: function(error) {
            console.error('Error fetching radio button options:', error);
        }
    });
}

populateRadioButtons();
populateStructureTypeDropdown();


// Function to check if the user is authenticated
async function checkAuthentication() {
  try {
    const response = await fetch('/auth', {
      method: 'GET',
      credentials: 'same-origin'
    });

    if (response.ok) {
      const data = await response.json();
      return data.data === 'True'; // Return true if authenticated, false otherwise
    } else if (response.status === 401) {
      return false; // User is not authenticated
    } else {
      throw new Error('Something went wrong!');
    }
  } catch (error) {
    console.error('Error:', error);
    return false; // Handle errors by returning false
  }
}


  function showAutocompleteSuggestions() {
        const input = document.getElementById('timer_name');
        const autocompleteList = document.getElementById('autocomplete_list');
        autocompleteList.innerHTML = '';

        // Fetch autocomplete suggestions from the server
        fetch('/api/autocomplete')
            .then(response => response.json())
            .then(data => {
                const suggestions = data;
                const inputText = input.value.toLowerCase();

                suggestions.forEach(suggestion => {
                    if (suggestion.toLowerCase().startsWith(inputText)) {
                        const suggestionItem = document.createElement('div');
                        suggestionItem.classList.add('autocomplete-item');
                        suggestionItem.innerText = suggestion;

                        suggestionItem.addEventListener('click', () => {
                            input.value = suggestion;
                            autocompleteList.innerHTML = '';
                        });

                        autocompleteList.appendChild(suggestionItem);
                    }
                });
            })
            .catch(error => console.error('Error fetching autocomplete suggestions:', error));
    }



    document.getElementById("countdown_form").addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const countdownDate = formData.get("countdown_date");
        const countdownTime = formData.get("countdown_time");
        const countdownDateTime = `${countdownDate} ${countdownTime}`;
        addCountdownTimer(countdownDateTime);

    });

     // Function to add a countdown timer
    function addCountdownTimer(countdownDateTime) {
        // Get timer name from the input field
        const timerNameInput = document.getElementById("timer_name");
        const timerName = timerNameInput.value || "Timer";

        const structure_typeInput = document.getElementById("structure_type");
        const structure_type = structure_typeInput.value;

        const userNameAuth = document.getElementById("username");
        const username = userNameAuth.innerHTML;


        const selectedRadioButton = document.querySelector('input[name="category"]:checked');
            // Check if a radio button is selected before accessing its value
        const selectedCategoryOption = selectedRadioButton ? selectedRadioButton.value : 'N/A';


        const newTimer = {
            name: timerName,
            type: structure_type,
            timerCat: selectedCategoryOption,
            countdownDate: countdownDateTime,
            authUserName: username
        };

        timers.push(newTimer);

        $.ajax({
            type: 'POST',
            url: '/api/create_timer',
            contentType: 'application/json',
            data: JSON.stringify({ 'timer_name': newTimer }),
            success: function(data) {
                console.log('Timer created successfully');
            }
        });






        saveTimersToServer(); // Save timers to the server, including the new timer
        displayTimers(); // Display the timers on the page
        timerNameInput.value = ''; // Clear the input field after adding the timer
        //location.reload();
    }

    function deleteTimer(index) {
        const timerCard = document.getElementById(`timer_${index + 1}`);
        timerCard.remove(); // Remove the entire timer card and its content from the DOM
        clearInterval(timers[index].countdownInterval);
        timers.splice(index, 1);
        displayTimers();
        saveTimersToServer();
       // removeEmptyCards(); // Remove any empty cards from the DOM
    }

    function removeEmptyCards() {
        const container = document.getElementById("timers_container");
        const cards = container.getElementsByClassName("card");
        for (let i = cards.length - 1; i >= 0; i--) {
            const timerText = cards[i].querySelector("h3").textContent.trim();
            if (!timerText) {
                cards[i].remove();
            }
        }
    }

    function updateTimerTitles() {
        const timerCards = document.getElementsByClassName("card-title");
        for (let i = 0; i < timerCards.length; i++) {
            timerCards[i].innerText = `Timer ${i + 1}`;
        }
    }

    function startCountdown(index) {
        const countdownDate = new Date(timers[index].countdownDate).getTime();
        const timerElement = document.getElementById(`timer_${index + 1}`);
        timers[index].timerElement = timerElement;

    function updateCountdown() {
            const now = new Date().getTime();
            const distance = countdownDate - now;

            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            timerElement.innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s ";

            if (distance < 0) {
                clearInterval(timers[index].countdownInterval);
                timerElement.innerHTML = "EXPIRED";
            }
        }

        updateCountdown();
        timers[index].countdownInterval = setInterval(updateCountdown, 1000);
    }

 // Function to display timers on the web page
    function displayTimers() {

 // Call the function to check authentication status
    checkAuthentication().then(isAuthenticated => {
      if (isAuthenticated) {
        console.log('User is authenticated!');
        const container = document.getElementById("timers_container");
        container.innerHTML = '';
        const structureTypeDropdown = document.getElementById("structure_type");
        // Sort the timers array by countdownDate in ascending order
        timers.sort((a, b) => new Date(a.countdownDate) - new Date(b.countdownDate));

       timers.forEach((timer, index) => {
            const timerCard = document.createElement("div");
            timerCard.classList.add("col-md-3", "mb-4");
            const endDateTime = new Date(timer.countdownDate).toLocaleString();
            const selectedImageSrc = timer.type.toLowerCase();
            let userName = timer.authUserName;
            let color = "red"
            if (timer.timerCat === "offensive") {
            color = "red";}
            else {
            color = "green";
            }
            timerCard.innerHTML = `
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${timer.name}</h5>

                        <h5 class="card-title">${timer.type}: <span style='color: ${color}'>${timer.timerCat}</span></h5>
                        <img src="/static/${selectedImageSrc}.jpg" alt="Structure Image" class="img-fluid rounded-circle">

                        <p class="card-text timer-expiry">End Date: ${endDateTime}</p>

                        <p class="card-text">By: ${userName}</p>
                        <h3 class="card-text" id="timer_${index + 1}"></h3>
                        <button class="btn btn-danger" onclick="deleteTimer(${index})">Delete</button>
                    </div>
                </div>
            `;


            container.appendChild(timerCard);
            startCountdown(index);
        });


        // Do something for authenticated users
      } else {
        console.log('User is not authenticated!');

        // Do something for non-authenticated users

      }});



    }



  // Function to save timers to the server using fetch API
    function saveTimersToServer() {
        fetch('/api/timers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ timers })
        })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error('Error saving timers:', error));
    }

    // Function to load timers from the server using fetch API
    function loadTimersFromServer() {

        checkAuthentication().then(isAuthenticated => {
      if (isAuthenticated) {
        console.log('User is authenticated!');
        fetch('/api/timers')
            .then(response => response.json())
            .then(data => {
                timers = data;
                displayTimers(); // Display the loaded timers on the page
            })
            .catch(error => console.error('Error loading timers:', error));
        // Do something for authenticated users
      } else {
        console.log('User is not authenticated!');

        const container = document.getElementById("login_button");
        var linkElement = document.createElement('a');
        linkElement.href = '/login'; // Replace with the actual URL

        // 3. Create an image element
        let imageElement = document.createElement('img');

// 4. Apply class and source to the image element
imageElement.classList.add('rounded-image');

        container.innerHTML = '';

        imageElement.classList.add('img-fluid');
        imageElement.src = 'static/eve-sso-login-white-large.png'; // Replace with the actual image path
// 5. Append the image element to the anchor element
linkElement.appendChild(imageElement);
// 4. Append the image element to the div's inner HTML
    container.appendChild(linkElement);

        // Do something for non-authenticated users

      }});


    }

        document.getElementById('timer_name').addEventListener('input', () => {
            showAutocompleteSuggestions();
        });

    // Load timers from the server on page load
    document.addEventListener('DOMContentLoaded', () => {
        loadTimersFromServer();
    });


