const priceMap = {
    "bill-5": 5,
    "bill-10": 10,
    "bill-20": 20,
    "bill-50": 50,
    "bill-100": 100,
    "bill-200": 200,
    "bill-500": 500,
    "bill-other": 1,
    "coin-200": 2,
    "coin-100": 1,
    "coin-50": 0.5,
    "coin-20": 0.2,
    "coin-10": 0.1,
    "coin-5": 0.05,
    "coin-2": 0.02,
    "coin-1": 0.01,
    "coin-other": 1,
};
var calculateTotal = function() {
    var runningTotal = 0;
    for (key in priceMap) {
	const value = document.querySelector('#' + key).value || 0;
	runningTotal += value * priceMap[key];
    }
    return runningTotal.toFixed(2)
};
document.querySelector("#calculator #resetInput").addEventListener("click", function() {
    for (key in priceMap) {
	document.querySelector('#' + key).value = 0;
    }
    document.querySelector("#calculator #calculatorResult").textContent = calculateTotal()
}, false);
document.querySelector("#calculator #useResult").addEventListener("click", function() {
    document.querySelector(".calculatable").value = calculateTotal()
}, false);
document.querySelectorAll("#calculator input").forEach(function (element) {
    element.addEventListener("input", function() {
	document.querySelector("#calculator #calculatorResult").textContent = calculateTotal()

    }, false)
});
document.querySelector("#calculator #calculatorResult").textContent = calculateTotal();
