import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    static targets = [ "email", "message" ];

    subscribe(event) {
        event.preventDefault();

        const email = this.emailTarget.value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/newsletter-signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                'email': email
            })
        })
        .then(response => response.json())
        .then(data => {
            this.messageTarget.textContent = data.message;
            if (data.success) {
                this.emailTarget.value = '';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.messageTarget.textContent = 'An error occurred. Please try again.';
        });
    }
}
