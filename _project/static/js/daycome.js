const dayincome = document.getElementById('dayincome');
const dayloses = document.getElementById('dayloses');
const daycheck = document.getElementById('daycheck');
const windowcon = document.getElementById('windowcon');
const detailcontainer = document.getElementById('detailcontainer');
const closedetwin = document.getElementById('closedetwin');
const sellsdel = document.querySelectorAll('#sellsdel');
const sellsup = document.querySelectorAll('#sellsup');
const rightconexpend = document.getElementById('rightconexpend')
const rightcon = document.querySelector('.rightcon')
//-----------------------------------------------------------------------------------------------------------
//right container menu size funcion 
rightconexpend.addEventListener('click',()=>{
    rightcon.classList.toggle( "active" );
})
//-----------------------------------------------------------------------------------------------------------
// Get all date input elements
const dateInputs = document.querySelectorAll('input[type="date"]');
// Get today's date
const today = new Date();
// Loop through each input and set its value to today's date
dateInputs.forEach(input => {
    input.value = today.toISOString().split('T')[0];
});
//---------------------------------------------------------------------------------
closedetwin.addEventListener('click',()=>{
    windowcon.style.top='0'
    windowcon.style.visibility='hidden'
    windowcon.style.opacity='0'
})
//-----------------------------------------------------------------------------------------------------------
sellsdel.forEach((sellsdel)=>{
    sellsdel.onclick=()=>{
        const metadata = sellsdel.getAttribute('metadata')
        windowcon.style.visibility = 'visible'
        windowcon.style.opacity = '1'
        document.getElementById('detailcontainer').innerHTML=metadata
        
    }
})
sellsup.forEach((sellsup)=>{
    sellsup.onclick=()=>{
        const metadata = sellsup.getAttribute('metadata')
        windowcon.style.visibility = 'visible'
        windowcon.style.opacity = '1'
        document.getElementById('detailcontainer').innerHTML=metadata
    }
})
//---------------------------------------------------------------------------------
dayincome.onclick=()=>{
    const metadata = dayincome.getAttribute('metadata')
    windowcon.style.visibility = 'visible'
    windowcon.style.opacity = '1'
    document.getElementById('detailcontainer').innerHTML=metadata
}
dayloses.onclick=()=>{
    const metadata = dayloses.getAttribute('metadata')
    windowcon.style.visibility = 'visible'
    windowcon.style.opacity = '1'
    document.getElementById('detailcontainer').innerHTML=metadata
}
daycheck.onclick=()=>{
    const metadata = daycheck.getAttribute('metadata')
    windowcon.style.visibility = 'visible'
    detailcontainer.style.width = '80%'
    windowcon.style.opacity = '1'
    document.getElementById('detailcontainer').innerHTML=metadata
}
function daycheckfun(){
    const day_remain = document.getElementById('day_remain');
    const day_income = document.getElementById('day_income');
    const day_loses = document.getElementById('day_loses');
    day_remain.value=parseFloat(day_income.value-day_loses.value);
}
function daycheckfun2(){
    const day_remain2= document.getElementById('day_remain2');
    const day_income2 = document.getElementById('day_income2');
    const day_loses2 = document.getElementById('day_loses2');
    day_remain2.value=parseFloat(day_income2.value-day_loses2.value);
}
