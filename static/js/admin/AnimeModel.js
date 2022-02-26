let source = document.querySelector('#id_source');
let genres = document.querySelector('#id_genres');
let themes = document.querySelector('#id_themes');
let author = document.querySelector('#id_author');
let description = document.querySelector('#id_description');
let original_name = document.querySelector('#id_item-0-original_name');
let english_name = document.querySelector('#id_item-0-english_name');
let russian_name = document.querySelector('#id_item-0-russian_name');
let title_manga = document.querySelector('#id_item-0-manga');
source.addEventListener('change', function (e) {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');
    if (source.value!=='') {
    let url = 'http://127.0.0.1:8000/api/manga/' + source.value+'/'
    let source_url = fetch(url).then(response => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
    }).then(data => {
        for (item of genres.options) {
            if (data.genres.includes(item.text)) {
                item.selected = true
            }
            else {
                item.selected = false
            }
        }

        for (item of themes.options) {
            if (data.themes.includes(item.text)) {
                item.selected = true
            }
            else {
                item.selected = false
            }
        }
        let name = data.author ? `${data.author.name} ${data.author.surname}` : '---------'
        const authors_opt = Array.from(author.options);
        const optionToSelect = authors_opt.find(item => item.text === name);
        optionToSelect.selected = true;


        description.value = data.description
        /*
        if (data.item) {
            original_name.value = data.item.original_name ? data.item.original_name : ''
            english_name.value = data.item.english_name ? data.item.english_name : ''
            russian_name.value = data.item.russian_name ? data.item.russian_name : ''
        }
        else {
            original_name.value = ''
            english_name.value = ''
            russian_name.value = ''

        }
        */
    }).catch(err => console.log(err));
    }
    else {
        for (item of genres.options) {
            item.selected = false
            }
        for (item of themes.options) {
            item.selected = false
            }
        author.selectedIndex = 0
        description.value = ''
        original_name.value = ''
        english_name.value = ''
        russian_name.value = ''
    }

})