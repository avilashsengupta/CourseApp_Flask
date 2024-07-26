let drop = false;
function menuDropDown() {
    if(drop == false) {
        document.getElementById('menu-drop').classList.remove('hidden');
        drop = true;
    }
    else {
        document.getElementById('menu-drop').classList.add('hidden');
        drop = false;
    }
}

function hideQuerySubmitSuccess() {
    document.getElementById('submit-success').classList.remove('flex');
    document.getElementById('submit-success').classList.add('hidden');
}

function hideQueryEnrollSuccess() {
    document.getElementById('enroll-success').classList.remove('flex');
    document.getElementById('enroll-success').classList.add('hidden');
}