-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 08, 2026 at 12:12 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ordering_management_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `attendance`
--

CREATE TABLE `attendance` (
  `attendance_id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `attendance_date` date NOT NULL,
  `time_in` time DEFAULT NULL,
  `time_out` time DEFAULT NULL,
  `status` enum('Present','Absent','Late') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

CREATE TABLE `customers` (
  `customer_id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `phone` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`customer_id`, `first_name`, `last_name`, `phone`) VALUES
(1, 'Ashley', 'Torres', '09201234567'),
(2, 'Faith', 'Macasojot', '09211234567'),
(3, 'Lei', 'Francisco', '09221234567');

-- --------------------------------------------------------

--
-- Table structure for table `employees`
--

CREATE TABLE `employees` (
  `employee_id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `position` varchar(50) NOT NULL,
  `date_hired` date DEFAULT NULL,
  `status` enum('Active','Inactive') NOT NULL DEFAULT 'Active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `employees`
--

INSERT INTO `employees` (`employee_id`, `first_name`, `last_name`, `phone`, `address`, `position`, `date_hired`, `status`) VALUES
(1, 'Jewel', 'Almeria', '09564061927', 'Nasugbu, Batangas', 'Owner/Admin', '2026-01-10', 'Active'),
(2, 'Jen', 'Francisco', '09817587551', 'Nasugbu, Batangas', 'Staff', '2026-02-15', 'Active'),
(3, 'Kat', 'Ignaco', '09536416277', 'Nasugbu, Batangas', 'Staff', '2026-03-01', 'Active');

-- --------------------------------------------------------

--
-- Table structure for table `expenses`
--

CREATE TABLE `expenses` (
  `expense_id` int(11) NOT NULL,
  `employee_id` int(11) DEFAULT NULL,
  `expense_date` datetime NOT NULL DEFAULT current_timestamp(),
  `expense_name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `menu_categories`
--

CREATE TABLE `menu_categories` (
  `category_id` int(11) NOT NULL,
  `category_name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `menu_categories`
--

INSERT INTO `menu_categories` (`category_id`, `category_name`, `description`) VALUES
(1, 'Beef', 'Beef dishes'),
(2, 'Pork', 'Pork dishes'),
(3, 'Kambing', 'Goat meat dishes'),
(4, 'Chicken', 'Chicken dishes'),
(5, 'Sea Foods', 'Seafood dishes'),
(6, 'Vegetable', 'Vegetable dishes'),
(7, 'Lomi', 'Lomi noodle dishes'),
(8, 'Beverage', 'Drinks and beverages'),
(9, 'Silog', 'Silog rice meals'),
(10, 'Pansit Bilao', 'Pancit served in bilao sizes'),
(11, 'Single Order', 'Individual noodle orders'),
(12, 'Additional', 'Additional rice and toppings');

-- --------------------------------------------------------

--
-- Table structure for table `menu_items`
--

CREATE TABLE `menu_items` (
  `item_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `item_name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `status` enum('Available','Unavailable') NOT NULL DEFAULT 'Available'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `menu_items`
--

INSERT INTO `menu_items` (`item_id`, `category_id`, `item_name`, `description`, `price`, `status`) VALUES
(1, 1, 'Bulalo', 'Beef soup dish', 600.00, 'Available'),
(2, 1, 'Sizzling Bulalo', 'Sizzling beef bulalo', 600.00, 'Available'),
(4, 1, 'Sinigang na Tadyang', 'Beef ribs cooked in sour soup', 550.00, 'Available'),
(5, 1, 'Kalderetang Baka', 'Beef cooked in tomato-based sauce', 550.00, 'Available'),
(6, 1, 'Kare-kareng Baka', 'Beef kare-kare', 550.00, 'Available'),
(7, 1, 'Gotong Batangas', 'Traditional Batangas beef dish', 120.00, 'Available'),
(8, 1, 'Papaitan', 'Traditional beef soup', 120.00, 'Available'),
(9, 2, 'Crispy Pata', 'Crispy fried pork leg', 600.00, 'Available'),
(10, 2, 'Grilled Liempo', 'Grilled pork belly', 160.00, 'Available'),
(11, 2, 'Pork Sinigang', 'Pork cooked in sour soup', 160.00, 'Available'),
(12, 2, 'Bicol Express', 'Pork cooked with coconut milk and chili', 160.00, 'Available'),
(13, 2, 'Binagoongan', 'Pork cooked with shrimp paste', 160.00, 'Available'),
(14, 2, 'Sizzling Sisig', 'Sizzling chopped pork sisig', 150.00, 'Available'),
(15, 2, 'Sizzling Tapa', 'Sizzling tapa', 150.00, 'Available'),
(16, 3, 'Kalderetang Kambing', 'Goat meat cooked in tomato-based sauce', 190.00, 'Available'),
(17, 3, 'Champening Kambing', 'Grilled goat meat', 190.00, 'Available'),
(18, 3, 'Sinampalukang Kambing', 'Goat meat cooked with tamarind', 190.00, 'Available'),
(19, 4, 'Grilled Chicken (Quarter Leg)', 'Grilled chicken quarter leg', 160.00, 'Available'),
(20, 4, 'Fried Chicken (Quarter Leg)', 'Fried chicken quarter leg', 160.00, 'Available'),
(21, 5, 'Sinigang na Hipon', 'Shrimp cooked in sour soup', 300.00, 'Available'),
(22, 5, 'Buttered Garlic Shrimp', 'Shrimp cooked with butter and garlic', 300.00, 'Available'),
(23, 5, 'Grilled Pusit', 'Grilled squid', 300.00, 'Available'),
(24, 5, 'Fish Fillet with Leaks', 'Fish fillet with leeks', 160.00, 'Available'),
(25, 5, 'Sinigang na Panga (Pink Salmon)', 'Pink salmon cooked in sour soup', 160.00, 'Available'),
(26, 5, 'Crunchy Dori', 'Crispy fried dory fish', 130.00, 'Available'),
(27, 6, 'Pinakbet', 'Mixed vegetables cooked Filipino-style', 80.00, 'Available'),
(28, 6, 'Chopsuey', 'Mixed vegetables with sauce', 120.00, 'Available'),
(29, 6, 'Laing', 'Taro leaves cooked in coconut milk', 120.00, 'Available'),
(30, 7, 'Lomi Regular', 'Regular serving of lomi', 75.00, 'Available'),
(31, 7, 'Lomi Special', 'Special serving of lomi', 125.00, 'Available'),
(32, 7, 'Lomi Barkada', 'Barkada-sized serving of lomi', 400.00, 'Available'),
(33, 8, '500ml Bottled Water', '500ml bottled water', 20.00, 'Available'),
(34, 8, '1L Bottled Water', '1 liter bottled water', 30.00, 'Available'),
(35, 8, 'Mismo', 'Mismo bottled drink', 25.00, 'Available'),
(36, 8, '1.5L Softdrinks', '1.5 liter soft drink', 100.00, 'Available'),
(37, 8, 'Pineapple Juice (in Can)', 'Canned pineapple juice', 50.00, 'Available'),
(38, 9, 'Silog', 'Silog meal', 50.00, 'Available'),
(39, 9, 'Bangsilog', 'Bangus, garlic rice and egg', 160.00, 'Available'),
(40, 9, 'Cornsilog', 'Corned beef, garlic rice and egg', 160.00, 'Available'),
(41, 9, 'Hotsilog', 'Hotdog, garlic rice and egg', 130.00, 'Available'),
(42, 9, 'Liempogsilog', 'Liempo, garlic rice and egg', 160.00, 'Available'),
(43, 9, 'Longsilog', 'Longganisa, garlic rice and egg', 130.00, 'Available'),
(44, 9, 'Sisig Rice', 'Sisig served with rice', 160.00, 'Available'),
(45, 9, 'Tapsilog', 'Tapa, garlic rice and egg', 160.00, 'Available'),
(46, 9, 'Tosilog', 'Tocino, garlic rice and egg', 160.00, 'Available'),
(47, 10, 'Small Sized Bilao', 'Small-sized pancit bilao', 450.00, 'Available'),
(48, 10, 'Medium Sized Bilao', 'Medium-sized pancit bilao', 800.00, 'Available'),
(49, 10, 'Large Sized Bilao', 'Large-sized pancit bilao', 1200.00, 'Available'),
(50, 10, 'XL Sized Bilao', 'Extra-large pancit bilao', 1450.00, 'Available'),
(51, 11, 'Pancit Canton', 'Single order of pancit canton', 120.00, 'Available'),
(52, 11, 'Pancit Bihon', 'Single order of pancit bihon', 120.00, 'Available'),
(53, 11, 'Mixed Canton & Bihon', 'Mixed pancit canton and bihon', 120.00, 'Available'),
(54, 11, 'Chami', 'Single order of chami', 160.00, 'Available'),
(55, 12, 'Garlic Rice', 'Additional garlic rice', 30.00, 'Available'),
(56, 12, 'Plain Rice', 'Additional plain rice', 25.00, 'Available'),
(57, 12, 'Garlic', 'Additional garlic', 10.00, 'Available'),
(58, 12, 'Onion', 'Additional onion', 10.00, 'Available'),
(59, 6, 'Pinakbet', 'Mixed vegetables cooked Filipino-style', 80.00, 'Available'),
(60, 6, 'Chopsuey', 'Mixed vegetables with sauce', 120.00, 'Available'),
(61, 6, 'Laing', 'Taro leaves cooked in coconut milk', 120.00, 'Available'),
(62, 7, 'Lomi Regular', 'Regular serving of lomi', 95.00, 'Available'),
(63, 7, 'Lomi Special', 'Special serving of lomi', 105.00, 'Available'),
(64, 7, 'Lomi Barkada', 'Barkada-sized serving of lomi', 400.00, 'Available'),
(65, 8, '500ml Bottled Water', '500ml bottled water', 20.00, 'Available'),
(66, 8, '1L Bottled Water', '1 liter bottled water', 30.00, 'Available'),
(67, 8, 'Mismo', 'Mismo bottled drink', 25.00, 'Available'),
(68, 8, '1.5L Softdrinks', '1.5 liter soft drink', 100.00, 'Available'),
(69, 8, 'Pineapple Juice (in Can)', 'Canned pineapple juice', 50.00, 'Available'),
(70, 9, 'Silog', 'Silog meal', 50.00, 'Available'),
(71, 9, 'Bangsilog', 'Bangus, garlic rice, and egg', 160.00, 'Available'),
(72, 9, 'Cornsilog', 'Corned beef, garlic rice, and egg', 160.00, 'Available'),
(73, 9, 'Hotsilog', 'Hotdog, garlic rice, and egg', 130.00, 'Available'),
(74, 9, 'Liempogsilog', 'Liempo, garlic rice, and egg', 160.00, 'Available'),
(75, 9, 'Longsilog', 'Longganisa, garlic rice, and egg', 130.00, 'Available'),
(76, 9, 'Sisig Rice', 'Pork Sisig (with egg), and Rice', 160.00, 'Available'),
(77, 9, 'Tapsilog', 'Tapa, garlic rice, and egg', 160.00, 'Available'),
(78, 9, 'Tosilog', 'Tocino, garlic rice, and egg', 160.00, 'Available');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `employee_id` int(11) NOT NULL,
  `table_id` int(11) DEFAULT NULL,
  `order_date` datetime NOT NULL DEFAULT current_timestamp(),
  `total_amount` decimal(10,2) NOT NULL DEFAULT 0.00,
  `order_status` enum('Pending','Completed','Cancelled') NOT NULL DEFAULT 'Pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `order_items`
--

CREATE TABLE `order_items` (
  `order_item_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

CREATE TABLE `payments` (
  `payment_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `payment_date` datetime NOT NULL DEFAULT current_timestamp(),
  `payment_method` enum('Cash','GCash','Card') NOT NULL,
  `amount_paid` decimal(10,2) NOT NULL,
  `payment_status` enum('Paid','Pending') NOT NULL DEFAULT 'Paid'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `restaurant_tables`
--

CREATE TABLE `restaurant_tables` (
  `table_id` int(11) NOT NULL,
  `table_number` varchar(20) NOT NULL,
  `capacity` int(11) DEFAULT NULL,
  `status` enum('Available','Occupied') NOT NULL DEFAULT 'Available'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `restaurant_tables`
--

INSERT INTO `restaurant_tables` (`table_id`, `table_number`, `capacity`, `status`) VALUES
(1, 'T01', 4, 'Available'),
(2, 'T02', 4, 'Available'),
(3, 'T03', 4, 'Available'),
(4, 'T04', 4, 'Available'),
(5, 'T05', 4, 'Available'),
(6, 'T06', 6, 'Available'),
(7, 'T07', 6, 'Available'),
(8, 'T08', 8, 'Available'),
(9, 'T09', 8, 'Available'),
(10, 'T10', 4, 'Available'),
(11, 'T11', 4, 'Available');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','staff') NOT NULL,
  `employee_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `password`, `role`, `employee_id`) VALUES
(1, 'admin', 'admin123', 'admin', 1),
(2, 'jen', 'staff123', 'staff', 2),
(3, 'kat', 'staff123', 'staff', 3);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`attendance_id`),
  ADD KEY `employee_id` (`employee_id`);

--
-- Indexes for table `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`customer_id`);

--
-- Indexes for table `employees`
--
ALTER TABLE `employees`
  ADD PRIMARY KEY (`employee_id`);

--
-- Indexes for table `expenses`
--
ALTER TABLE `expenses`
  ADD PRIMARY KEY (`expense_id`),
  ADD KEY `employee_id` (`employee_id`);

--
-- Indexes for table `menu_categories`
--
ALTER TABLE `menu_categories`
  ADD PRIMARY KEY (`category_id`),
  ADD UNIQUE KEY `category_name` (`category_name`);

--
-- Indexes for table `menu_items`
--
ALTER TABLE `menu_items`
  ADD PRIMARY KEY (`item_id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `employee_id` (`employee_id`),
  ADD KEY `table_id` (`table_id`);

--
-- Indexes for table `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`order_item_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `item_id` (`item_id`);

--
-- Indexes for table `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`payment_id`),
  ADD KEY `order_id` (`order_id`);

--
-- Indexes for table `restaurant_tables`
--
ALTER TABLE `restaurant_tables`
  ADD PRIMARY KEY (`table_id`),
  ADD UNIQUE KEY `table_number` (`table_number`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `employee_id` (`employee_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `attendance`
--
ALTER TABLE `attendance`
  MODIFY `attendance_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `customers`
--
ALTER TABLE `customers`
  MODIFY `customer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `employees`
--
ALTER TABLE `employees`
  MODIFY `employee_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `expenses`
--
ALTER TABLE `expenses`
  MODIFY `expense_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `menu_categories`
--
ALTER TABLE `menu_categories`
  MODIFY `category_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `menu_items`
--
ALTER TABLE `menu_items`
  MODIFY `item_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=79;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `order_items`
--
ALTER TABLE `order_items`
  MODIFY `order_item_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `payments`
--
ALTER TABLE `payments`
  MODIFY `payment_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `restaurant_tables`
--
ALTER TABLE `restaurant_tables`
  MODIFY `table_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `attendance`
--
ALTER TABLE `attendance`
  ADD CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `expenses`
--
ALTER TABLE `expenses`
  ADD CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `menu_items`
--
ALTER TABLE `menu_items`
  ADD CONSTRAINT `menu_items_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `menu_categories` (`category_id`) ON UPDATE CASCADE;

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`table_id`) REFERENCES `restaurant_tables` (`table_id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `menu_items` (`item_id`) ON UPDATE CASCADE;

--
-- Constraints for table `payments`
--
ALTER TABLE `payments`
  ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
