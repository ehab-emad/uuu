export class ExpirationChecker {
    constructor(expirationTime, url) {
        this.url = url; // Django URL to send the request
        this.expirationTime = expirationTime
        this._startExpirationTimer(); // Start the "thread" on instantiation
    }

    _startExpirationTimer() {
        // Start the timer function to check expiration
        this._timerId = setInterval(() => this._timerFunction(), 1000); // Check every second
    }

    _timerFunction() {
        const currentTimestamp = Math.floor(Date.now() / 1000);
        this._printExpirationTime(currentTimestamp)
        
        if (currentTimestamp >= this.expirationTime) {
            console.log('Expiration time reached. Sending request...');
            this.sendRequest();
            clearInterval(this._timerId); // Stop the timer after sending the request
        }
    }

    _printExpirationTime(currentTimestamp) {
        const watermarkElement = document.querySelector('.expirationWatermark p');
        const differenceInSeconds = this.expirationTime - currentTimestamp;
        const minutes = Math.floor(differenceInSeconds / 60);
        const seconds = differenceInSeconds % 60;
        watermarkElement.innerText = `Session expires in ${minutes} minute(s) and ${seconds} second(s)`
        console.log(`Session expires in ${minutes} minute(s) and ${seconds} second(s)`)
    }

    sendRequest() {
        debugger;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        var redirect_url = 'keycloak/expired_login/';
        $.ajax({                       // initialize an AJAX request
            type:'POST',
            headers: { 'X-CSRFToken': csrftoken },        
            url: redirect_url,
            data: {},
            success: function (data) {
                window.location.reload();
            }
          });
    }
}
