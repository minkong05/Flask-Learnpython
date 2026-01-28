document.addEventListener('DOMContentLoaded', () => {
    const menuIcon = document.getElementById('menuIcon');
    if (menuIcon) {
        menuIcon.addEventListener('click', () => {
            const mobileMenu = document.getElementById('mobileMenu');
            if (mobileMenu) {
                mobileMenu.style.display = (mobileMenu.style.display === 'block') ? 'none' : 'block';
            }
        });
    }

    const scrollToTopButton = document.getElementById('scrollToTop');
    if (scrollToTopButton) {
        scrollToTopButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth',
            });
        });
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

            const email = document.getElementById('registerEmail').value.trim();
            const username = document.getElementById('registerUsername').value.trim();
            const password = document.getElementById('registerPassword').value.trim();
            const confirmPassword = document.getElementById('confirmPassword').value.trim();

            if (!email || !username || !password || !confirmPassword) {
                alert('Please fill in all fields.');
                return;
            }

            if (password !== confirmPassword) {
                alert('Passwords do not match.');
                return;
            }

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                                'Content-Type': 'application/json',
                                'X-CSRF-Token': csrfToken
                            },
                    body: JSON.stringify({ email, username, password }),
                });

                const result = await response.json();
                if (response.ok && result.status === 'success') {
                    window.location.href = '/login';
                } else {
                    console.error('Registration failed:', result.message);
                    alert(`Registration failed: ${result.message}`);
                }
            } catch (error) {
                console.error('Error during registration:', error);
                alert('An error occurred during registration. Please try again.');
            }
        });
    }

    
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

            const email = document.getElementById('loginEmail').value.trim();
            const password = document.getElementById('loginPassword').value.trim();

            if (!email || !password) {
                alert('Please fill in all fields.');
                return;
            }

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                                'Content-Type': 'application/json',
                                'X-CSRF-Token': csrfToken
                            },
                    body: JSON.stringify({ email, password }),
                });

                const result = await response.json();
                if (response.ok && result.status === 'success') {
                    window.location.href = '/unlock';
                } else {
                    console.error('Login failed:', result.message);
                    alert(`Login failed: ${result.message}`);
                }
            } catch (error) {
                console.error('Error during login:', error);
                alert('An error occurred during login. Please try again.');
            }
        });
    }
});




document.addEventListener("DOMContentLoaded", function () {
    // Select all links with the class 'smooth-scroll
    const links = document.querySelectorAll('.smooth-scroll');

    links.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent the default anchor jump behavior
            const targetId = this.getAttribute('href').substring(1); // Get the target ID
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' }); // Smooth scroll to the target
            }
        });
    });
});



document.addEventListener("DOMContentLoaded", function () {
    // Check if the URL contains a hash
    const hash = window.location.hash;

    if (hash) {
        // Find the corresponding target element
        const target = document.querySelector(hash);
        if (target) {
            // Perform smooth scrolling
            setTimeout(() => {
                target.scrollIntoView({ behavior: 'smooth' });
            }, 100); // Delay scrolling to ensure the page is fully loaded
        }
    }
});



document.getElementById("profileButton").addEventListener("click", () => {
    const profileDetails = document.getElementById("profileDetails");

    // Toggle show or hide
    if (profileDetails.classList.contains("hidden")) {
        // Get user information and display it
        fetch('/get_user_profile')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById("userName").textContent = data.user.username;
                    document.getElementById("userEmail").textContent = data.user.email;
                    document.getElementById("userTier").textContent = data.user.tier_name;
                    document.getElementById("userAiquota").textContent = 20-(data.user.query_count);
                } else {
                    alert("Failed to load user profile.");
                }
            })
            .catch(err => {
                console.error("Error fetching profile:", err);
                alert("An error occurred while fetching user profile.");
            });

        profileDetails.classList.remove("hidden");
        profileDetails.style.display = "block";
    } else {
        profileDetails.classList.add("hidden");
        profileDetails.style.display = "none";
    }
});


document.addEventListener("click", (event) => {
    const profileMenu = document.getElementById("profileDetails");
    if (!event.target.closest(".profile-menu")) {
        profileMenu.classList.add("hidden");
        profileMenu.style.display = "none";
    }
});

