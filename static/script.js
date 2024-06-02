function customSubmit() {
    let platform = document.getElementsByName('platform')[0]
    let python_version = document.getElementsByName('python_version')[0]
    let package = document.getElementsByName('package')[0]
    globalThis.PACKAGE = package.value

    let busy = document.getElementById('busy')

    let data = {
        platform: platform.options[platform.selectedIndex].value,
        python_version: python_version.options[python_version.selectedIndex].value,
        package: package.value
    }

    let url = window.location.href
    let method = 'POST'

    const xhr = new XMLHttpRequest();
    xhr.open(method, url)
    xhr.onload = () => {
        busy.style.display = 'none'
        if (xhr.readyState == 4 && xhr.status == 200) {
            parse_data(JSON.parse(xhr.responseText))
        } else {
            console.log(`Error: ${xhr.status}`);
        }
    }

    clear_package_list()
    busy.style.display = 'block'

    xhr.send(JSON.stringify(data))
}


function parse_data(data) {
    globalThis.KEY = data.key

    let list = document.getElementById('package_list')

    if (data['packages'].length === 0) {
        let li = document.createElement('li')
        li.innerText = 'Packages not found'
        list.appendChild(li)
        return
    }

    let download_button = document.getElementById('download_all')
    download_button.style.visibility = 'visible'

    data['packages'].forEach(pack => {
        let url = `/package?key=${data.key}&name=${pack}`
        list.appendChild(create_package_item(pack, url))
    })
}


function clear_package_list() {
    let list = document.getElementById('package_list')
    list.innerHTML = ''
}


function submit(field) {
    if (field.key === 'Enter') {
        customSubmit()
    }
}


function downloadArchive() {
    console.log(globalThis.KEY)
    url = window.location.origin + `/archive?key=${globalThis.KEY}&name=${globalThis.PACKAGE}`
    window.location.href = url
}


function create_package_item(name, url) {
    let li = document.createElement('li')
    let a = document.createElement('a')
    a.innerText = name
    a.href = url
    li.appendChild(a)
    return li
}
