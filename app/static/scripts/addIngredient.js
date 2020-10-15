// Get elements from DOM
let area = document.getElementById('ingredients-box');
let quantity = document.getElementById('quantity');
let ingredient = document.getElementById('ingredient');

// Counter to differentiate id's
let counter = 0;

// Inserts newNode after referenceNode
function insertAfter(referenceNode, newNode) {
  referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

// Checks if quantity is an integer greater than zero
function validateQuantity(number){
  let reg = /\d*/;
  return (reg.test(number) && number > 0);
}

// Reads quantity and ingredient name, and appends it to the DOM
function addIngredient(){
  if (validateQuantity(quantity.value)){
    // Get last container in form, before save button
    children = area.children;
    child = children[children.length - 2];
    
    // Create delete button with class and id
    let button = document.createElement('BUTTON'); 
    button.classList.add("delete-button");
    button.classList.add("btn");
    button.classList.add("btn-danger");
    button.textContent = "-";
    button.id = "delete-" + counter;
    button.setAttribute("onclick", "deleteIngredient(this)");

    // Create flex container to hold button and paragragh in same line
    let container = document.createElement("div");
    container.classList.add("wraper");
    container.classList.add("inline-flex");
    container.id = "container-" + counter;

    // Create text input to hold quantity and ingredient information
    let tag = document.createElement("INPUT");
    tag.setAttribute("type", "text");
    tag.setAttribute("readOnly", "true");
    tag.setAttribute("name", 'ingredient' + counter);
    tag.defaultValue = quantity.value + ' ' + ingredient.value;
    tag.classList.add('ingredient');

    // Clear input fields
    quantity.value = '';
    ingredient.value = '';

    // Append ingredient to recipe
    container.appendChild(button);
    container.appendChild(tag);

    // If form has at least 1 ingredient
    if (children.length >= 2){
      insertAfter(child, container);
    } else if (children.length === 1) {
      area.insertBefore(container, children[0]);
    }
    else {
      area.appendChild(container);
    }

    // Get save button if exists. Otherwise, create it along with a form to post data
    let saveButton = document.getElementById('save-button');
    if (!saveButton){
      let container = document.getElementById("buttons-container"); 

      // Create sumbit button for form
      saveButton = document.createElement('BUTTON');
      saveButton.setAttribute("type", "submit"); 
      saveButton.setAttribute("value", "Submit"); 
      saveButton.id = 'save-button';
      saveButton.classList.add('btn');
      saveButton.classList.add('btn-info');
      saveButton.textContent = 'Save Recipe';

      // Append button to form
      container.appendChild(saveButton);
    }

    counter++;
  }
  else{
    console.log('Error');
  }
}

// Identifies id number of button, and deletes the container with the same number
function deleteIngredient(element){
  // Get id number of element that called the function
  let id = element.id;
  let id_number = id[id.length - 1];

  // Delete container with same id number
  let container = document.getElementById("container-" + id_number)
  container.remove();
}

// Right before submit get the recipe's name and add it to the form
function addRecipeName(){
  console.log("I'm in");
  // Get recipe's name from previous element
  let recipe = document.getElementById('recipe-name');

  // Get form element
  let form = document.getElementById('ingredients-box');

  // Create input element
  let input = document.createElement("INPUT");
  input.setAttribute("type", "text");
  input.setAttribute("readOnly", "true");
  input.setAttribute("name", 'recipe');
  input.defaultValue = recipe.value;
  input.id = 'recipe';

  // Append recipe name to form
  form.appendChild(input);

  return true;

}

// Gets all ingredients and calls the same page with a POST request to save it
function saveRecipe(){
  // Gets all spans containing ingredients
  let spans = document.getElementsByClassName('ingredient');
  let len = spans.length;
  
  // Creates array to hold ingredients
  let ingredients = []

  // Saves ingredients into array to POST it
  for (let i = 0; i < len; i++){
    ingredients.push(spans[i].textContent);
  }
  return 
}