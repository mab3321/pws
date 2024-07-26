function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}
async function setDropdownValueAndTriggerChange(options) {
  const { id, value, timeout = 10000 } = options;
  // Polling function to wait for the element to appear
  async function waitForElement() {
    const startTime = Date.now(); // Record the start time

    // Repeatedly check for the element's existence until it appears or timeout is reached
    while (true) {
      if (Date.now() - startTime > timeout) {
        // Check if timeout is reached
        throw new Error(`Timeout waiting for element with ID '${id}'`);
      }
      const element = document.getElementById(id);
      if (element) {
        return element;
      }
      await sleep(3000); // Wait for 100 milliseconds before checking again
    }
  }
  // Get the dropdown element by ID
  var element = await waitForElement();
  // Set the value
  element.value = value;

  // Trigger the change event
  var event = new Event("change", { bubbles: true });
  element.dispatchEvent(event);

  // Wait for 2 seconds
  await sleep(2000);
}
async function setDropdownByNameAndTriggerChange(options) {
  const { id, name, timeout = 10000 } = options;
  // Polling function to wait for the element to appear
  async function waitForElement() {
    const startTime = Date.now(); // Record the start time

    // Repeatedly check for the element's existence until it appears or timeout is reached
    while (true) {
      if (Date.now() - startTime > timeout) {
        // Check if timeout is reached
        throw new Error(`Timeout waiting for element with ID '${id}'`);
      }
      const element = document.getElementById(id);
      if (element) {
        return element;
      }
      await sleep(3000); // Wait for 100 milliseconds before checking again
    }
  }
  // Get the dropdown element by ID
  var element = await waitForElement();

  var options = element.options;

  for (var i = 0; i < options.length; i++) {
    if (options[i].text === name) {
      options[i].selected = true;
      // Trigger the change event
      var event = new Event("change", { bubbles: true });
      element.dispatchEvent(event);
      break;
    }
  }

  // Wait for 2 seconds
  await sleep(2000);
}

async function main() {

  await setDropdownValueAndTriggerChange({
    id: "ctl00_ContentPlaceHolder2_GdInfoSeaUc_ddlPortOfDischarge",
    value: "41846",
  });

  return true;
}
await main();
