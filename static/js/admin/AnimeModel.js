let source = document.querySelector("#select2-id_source-container")
console.log(source)
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
    if (source.value !== '') {
        let url = 'http://127.0.0.1:8000/api/manga/' + source.value + '/'
        let source_url = fetch(url).then(response => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
        }).then(data => {
            console.log(source)
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
        /*
        description.value = ''
        original_name.value = ''
        english_name.value = ''
        russian_name.value = ''
        */
    }

})

function invoke_reply(id) {
    if (document.contains(document.getElementById("newForm"))) { 
        if (document.getElementById("newForm").parentNode.parentNode.id==id) {
            return formExit();
        } else {
            formExit();
        }
      }
      const parent_id = document.getElementById(id);
      const children=parent_id.querySelector('.children')
      const placeholder = document.createElement("div");
        placeholder.innerHTML = `<form id="newForm" class="form-insert py-2" method="post"> \
            <div class="d-flex justify-content-between"><h2>Reply:</h2> \
            <select name="parent" class="d-none" id="id_parentt" hidden> \
            <option value=${id} selected=${id}></option> \
            </select> \
            <textarea name="content" cols="40" rows="5" class="form-control" required id="id_content"></textarea> \
            {% csrf_token %} \
            <button type="submit" onclick="comment_submit(event,id)" >Submit</button> \
          </form>`;
      parent_id.insertBefore(placeholder,children)
}

function delete_comment(id) {
    const csrftoken = getCookie('csrftoken');
    const url = 'http://127.0.0.1:8000/blog/comment/' + id +'/delete/'
    let source_url = fetch(url, {
        method: 'POST',
        headers: { "X-CSRFToken": csrftoken }
    }).then(response => {
        if (!response.ok) throw Error(response.statusText);
        let com=document.getElementById(id);
        com.remove();
        return response.json();
    })
}

function comment_submit(e, id ) {
    let comment_btn = id!== undefined ? document.querySelector('#newForm'):document.querySelector('#myDIV');
    e.preventDefault()
    const csrftoken = getCookie('csrftoken');
    const url = 'http://127.0.0.1:8000/blog/comment/' + '{{post.id}}/'
    let data = new FormData();
    let content = comment_btn.querySelector('#id_content').value
    let parent = comment_btn.querySelector('#id_parentt')
    data.append('author', {{request.user.id}})
    data.append('content', content)
    if (parent) {
        parent = parent.options[parent.selectedIndex].value;
        data.append('parent', parent)
        }
    let source_url = fetch(url, {
        method: 'POST',
        body: data,
        headers: { "X-CSRFToken": csrftoken }
    }).then(response => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
    }).then(json => {
        let comments = id==undefined? document.querySelector('.comments') : comment_btn.parentNode.parentNode.querySelector('.children');
        let elem=document.createElement('div')
        elem.setAttribute('id',`${json.id}`)
        let date= new Date(json.created)
        let data='date.getMonth()' + 'date.getDay()' + 'date.getHours()' + 'date.getMinutes()';
        elem.innerHTML = `<div class="">By ${json.author}</div>
        <div>${data}</div>
        <div>${content}</div>
        <button class="button" onclick="invoke_reply(${json.id})">Reply</button>
        <button class="button" onclick="delete_comment(${json.id})">Delete</button>
        <div class="children"></div>`
        comments.appendChild(elem)   
        formExit();     
    })
}

commentsConsumer.onmessage = function(e) {
    const data= JSON.parse(e.data)
    console.log(data)
    //let  comments = data['message']['id']==undefined? document.querySelector('.comments') : comment_btn.parentNode.parentNode.querySelector('.children');
    let  comments = document.querySelector('.comments') 
    let elem=document.createElement('div')
    elem.setAttribute('id',`${data['message']['id']}`)
    elem.innerHTML = `<div class="comment-upper">
        <div class="base-img"><img src="/media/${data['message']['author_image']}" ></div>
        <div class="comment-upper-info">
    <div class="">By ${data['message']['author']}</div>
    <div>${data['message']['created']}</div>
</div>
</div>
    <div class="comment-content">${data['message']['content']}</div>
    <button class="button" onclick="invoke_reply(${data['message']['id']})">Reply</button>
    <button class="button" onclick="delete_comment(${data['message']['id']})">Delete</button>
    <div class="children"></div>`
    comments.appendChild(elem)
    formExit(); 
}
