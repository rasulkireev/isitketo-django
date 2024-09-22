// app/javascript/controllers/search_controller.js

import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
  static targets = [ "input", "results" ];
  static values = {
    url: String,
    mediaPrefix: String
  };

  connect() {
    this.timeout = null;
    this.doneTypingInterval = 300; // ms
    this.styleResults();
    this.hideResults();
    this.bindGlobalEvents();
  }

  disconnect() {
    this.unbindGlobalEvents();
  }

  bindGlobalEvents() {
    this.onClickOutside = this.onClickOutside.bind(this);
    document.addEventListener('click', this.onClickOutside);

    this.onKeyDown = this.onKeyDown.bind(this);
    document.addEventListener('keydown', this.onKeyDown);
  }

  unbindGlobalEvents() {
    document.removeEventListener('click', this.onClickOutside);
    document.removeEventListener('keydown', this.onKeyDown);
  }

  onClickOutside(event) {
    if (!this.element.contains(event.target)) {
      this.hideResults();
    }
  }

  onKeyDown(event) {
    if (event.key === 'Escape') {
      this.hideResults();
    } else if (event.key === 'Enter' && document.activeElement === this.inputTarget) {
      event.preventDefault();
      this.handleEnter();
    }
  }

  handleEnter() {
    const firstResult = this.resultsTarget.querySelector('li a');
    if (firstResult) {
      window.location.href = firstResult.href;
    } else {
      this.clearSearch();
    }
  }

  styleResults() {
    const style = {
      position: 'absolute',
      zIndex: '1000',
      backgroundColor: 'white',
      border: '1px solid #e5e7eb',
      borderRadius: '0.375rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      maxHeight: '300px',
      overflowY: 'auto',
      width: '100%',
      marginTop: '0.25rem',
    };

    Object.assign(this.resultsTarget.style, style);
  }

  hideResults() {
    this.resultsTarget.style.display = 'none';
  }

  showResults() {
    this.resultsTarget.style.display = 'block';
  }

  search() {
    clearTimeout(this.timeout);
    this.timeout = setTimeout(() => {
      this.performSearch();
    }, this.doneTypingInterval);
  }

  async performSearch() {
    const query = this.inputTarget.value;
    if (query.length > 2) {
      try {
        const response = await fetch(`${this.urlValue}?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        this.displayResults(data);
      } catch (error) {
        console.error('Error:', error);
      }
    } else {
      this.hideResults();
    }
  }

  displayResults(data) {
    if (data.length > 0) {
      const html = data.map(item => `
        <li class="px-4 py-2 cursor-pointer hover:bg-gray-100">
          <a href="/${item.slug}" data-action="click->search#clearSearch" class="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
            <img src="${this.mediaPrefixValue}${item.compressed_image}" alt="${item.name}" loading="lazy" class="object-cover flex-shrink-0 mr-2 w-6 h-6 rounded-full">
            <span class="truncate">${item.name}</span>
          </a>
        </li>
      `).join('');
      this.resultsTarget.innerHTML = `<ul class="p-0 m-0 list-none">${html}</ul>`;
      this.showResults();
    } else {
      this.resultsTarget.innerHTML = '<p class="px-4 py-2 text-gray-500">No results found</p>';
      this.showResults();
    }
  }

  clearSearch() {
    this.inputTarget.value = '';
    this.hideResults();
  }
}
