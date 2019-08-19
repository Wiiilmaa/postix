
const priceMap = {
    "id_bills_automated-0-bill_5": 5,
    "id_bills_automated-0-bill_10": 10,
    "id_bills_automated-0-bill_20": 20,
    "id_bills_automated-0-bill_50": 50,
    "id_bills_automated-0-bill_100": 100,
    "id_bills_automated-0-bill_200": 200,
    "id_bills_automated-0-bill_500": 500,
    "id_bills_bulk-0-bill_500": 500,
    "id_bills_bulk-0-bill_1000": 1000,
    "id_bills_bulk-0-bill_2000": 2000,
    "id_bills_bulk-0-bill_5000": 5000,
    "id_bills_bulk-0-bill_10000": 10000,
    "id_bills_bulk-0-bill_20000": 20000,
    "id_bills_bulk-0-bill_50000": 50000,
    "id_bills_manually-0-bill_5": 5,
    "id_bills_manually-0-bill_10": 10,
    "id_bills_manually-0-bill_20": 20,
    "id_bills_manually-0-bill_50": 50,
    "id_bills_manually-0-bill_100": 100,
    "id_bills_manually-0-bill_200": 200,
    "id_bills_manually-0-bill_500": 500,
    "id_coins_automated-0-coin_200": 2,
    "id_coins_automated-0-coin_100": 1,
    "id_coins_automated-0-coin_50": 0.5,
    "id_coins_automated-0-coin_20": 0.2,
    "id_coins_automated-0-coin_10": 0.1,
    "id_coins_automated-0-coin_5": 0.05,
    "id_coins_automated-0-coin_2": 0.02,
    "id_coins_automated-0-coin_1": 0.01,
    "id_coins_bulk-0-coin_5000": 50,
    "id_coins_bulk-0-coin_2000": 20,
    "id_coins_bulk-0-coin_2500": 25,
    "id_coins_bulk-0-coin_800": 8,
    "id_coins_bulk-0-coin_250": 2.5,
    "id_coins_bulk-0-coin_400": 4,
    "id_coins_bulk-0-coin_100": 1,
    "id_coins_bulk-0-coin_50": 0.5,
};
var calculateTotal = function() {
    var runningTotal = 0;
    for (var element of document.querySelectorAll('.balance-card input[type=number]')) {
	if (!element.value) continue
	const factor = element.id.includes('coins') ? 100 : 1;
	const value = Number(element.id.substring(element.id.lastIndexOf('_') + 1))/factor;
	runningTotal += value * element.value
    };
    return runningTotal.toFixed(2)
};
var calculateDifference = function() {
    var difference = 0;
    var expected = Number(document.querySelector("#balance-expected").getAttribute("data-value"));
    var actual = calculateTotal();

    difference = actual - expected;

    return difference.toFixed(2);
};
var decimal_separator = (
  document.querySelector("#balance-expected").textContent.indexOf(",") > 0 ? "," : "."
);
for (var element of document.querySelectorAll("#balance-form input")) {
  element.addEventListener("input", function() {
    document.querySelector("#calculator-result").textContent = calculateTotal().replace(".", decimal_separator);
    document.querySelector("#calculator-difference-result").textContent = calculateDifference().replace(".", decimal_separator);
  }, false)
};
document.querySelector("#calculator-result").textContent = calculateTotal().replace(".", decimal_separator);
document.querySelector("#calculator-difference-result").textContent = calculateDifference().replace(".", decimal_separator);

document.querySelector('#id_coins_bulk-TOTAL_FORMS').value = 1;
document.querySelector('#id_coins_automated-TOTAL_FORMS').value = 1;
document.querySelector('#id_bills_bulk-TOTAL_FORMS').value = 1;
document.querySelector('#id_bills_automated-TOTAL_FORMS').value = 1;
document.querySelector('#id_bills_manually-TOTAL_FORMS').value = 1;

for (var element of document.querySelectorAll("a.add-form")) {
    element.addEventListener("click", function(e) {
	const currentElement = e.currentTarget;
	const title = currentElement.id.substring(0, currentElement.id.lastIndexOf('-'));
	const form_count = document.querySelectorAll('.balance-card.' + title).length;
	const template = document.querySelector('#template .balance-card.' + title);
	const new_form = template.outerHTML.replace(/__prefix__/g, form_count - 1);
	document.querySelector('#id_' + title.replace('-', '_') + '-TOTAL_FORMS').value = form_count;
	document.querySelector('.balance-card.' + title).insertAdjacentHTML('beforebegin', new_form);
	for (var innerElement of document.querySelectorAll("#balance-form .balance-card." + title + " input")) {
	    innerElement.addEventListener("input", function() {
		document.querySelector("#calculator-result").textContent = calculateTotal();
		document.querySelector("#calculator-difference-result").textContent = calculateDifference();
	    }, false)
	}
    })
};
