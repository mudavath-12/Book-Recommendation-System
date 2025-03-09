document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('searchButton');
    const bookTitleInput = document.getElementById('bookTitle');
    const recommendationsDiv = document.getElementById('recommendations');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');

    function createBookCard(book) {
        const card = document.createElement('div');
        card.className = 'book-card';
        
        const image = document.createElement('img');
        image.src = book.image_url;
        image.alt = book.title;
        image.className = 'book-image';
        image.onerror = () => {
            image.src = "https://via.placeholder.com/200x300?text=No+Image";
        };

        const info = document.createElement('div');
        info.className = 'book-info';

        const title = document.createElement('h2');
        title.className = 'book-title';
        title.textContent = book.title;

        const authors = document.createElement('div');
        authors.className = 'book-authors';
        authors.textContent = `By ${book.authors.join(', ')}`;

        const subjects = document.createElement('div');
        subjects.className = 'book-subjects';
        book.subjects.forEach(subject => {
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.textContent = subject;
            subjects.appendChild(tag);
        });

        const description = document.createElement('p');
        description.className = 'book-description';
        description.textContent = book.description || 'No description available';

        info.appendChild(title);
        info.appendChild(authors);
        info.appendChild(subjects);
        info.appendChild(description);

        card.appendChild(image);
        card.appendChild(info);

        return card;
    }
    

    async function searchBooks() {
        try {
            loadingDiv.classList.remove('hidden');
            errorDiv.classList.add('hidden');
            recommendationsDiv.innerHTML = '';

            const response = await fetch(`/api/recommendations?title=${encodeURIComponent(bookTitleInput.value)}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Error fetching recommendations');
            }

            if (data.recommendations.length === 0) {
                errorDiv.textContent = 'No books found';
                errorDiv.classList.remove('hidden');
                return;
            }

            data.recommendations.forEach(book => {
                const bookCard = createBookCard(book);
                recommendationsDiv.appendChild(bookCard);
            });

        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.classList.remove('hidden');
        } finally {
            loadingDiv.classList.add('hidden');
        }
    }

    searchButton.addEventListener('click', searchBooks);
    bookTitleInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchBooks();
    });

    
});