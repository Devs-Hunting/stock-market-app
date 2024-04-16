  let display_menu = false;

  function toggle_menu(){
      display_menu = !display_menu;
      if(display_menu) {
        document.getElementById("navbarBurger").classList.add('is-active');
        document.getElementById("navbarBasic").classList.add('is-active');
      }
      else
      {
        document.getElementById("navbarBurger").classList.remove('is-active');
        document.getElementById("navbarBasic").classList.remove('is-active');
      }
  }
