-- 创建数据库
CREATE DATABASE IF NOT EXISTS campus_secondhand41 DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE campus_secondhand41;

-- 1. 用户表（加后缀41）
CREATE TABLE `user41` (
  `user_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID（主键）',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名（非空）',
  `password` VARCHAR(100) NOT NULL COMMENT '密码（非空，加密存储）',
  `role` ENUM('admin','user') NOT NULL DEFAULT 'user' COMMENT '角色：管理员/普通用户（非空）',
  `phone` VARCHAR(20) COMMENT '手机号（允许空）',
  `email` VARCHAR(50) COMMENT '邮箱（允许空）',
  `status` ENUM('normal','frozen') NOT NULL DEFAULT 'normal' COMMENT '账号状态（非空）',
  `register_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间（非空）',
  CONSTRAINT `uk_username41` UNIQUE (`username`)
) COMMENT '用户表';

-- 2. 物品类别表（加后缀41）
CREATE TABLE `category41` (
  `category_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '类别ID（主键）',
  `category_name` VARCHAR(50) NOT NULL COMMENT '类别名称（非空）',
  `description` VARCHAR(200) COMMENT '类别描述（允许空）',
  CONSTRAINT `uk_category_name41` UNIQUE (`category_name`)
) COMMENT '物品类别表';

-- 初始化类别数据
INSERT INTO category41 (category_name, description) VALUES 
('书籍教材', '大中小学教材、课外书籍、考研考公资料'),
('电子产品', '手机、电脑、平板、耳机、充电器等'),
('生活用品', '床品、收纳、厨具、洗护用品等'),
('体育用品', '篮球、羽毛球拍、瑜伽垫、运动服等'),
('美妆护肤', '口红、粉底液、面霜、面膜等（全新/九成新）'),
('服装鞋帽', '上衣、裤子、鞋子、帽子、包包等'),
('学习用品', '笔、笔记本、文件夹、台灯、计算器等'),
('其他物品', '未分类的二手物品');

-- 3. 二手物品表（加后缀41）
CREATE TABLE `goods41` (
  `goods_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '物品ID（主键）',
  `category_id` INT NOT NULL COMMENT '类别ID（外键）',
  `publisher_id` INT NOT NULL COMMENT '发布者ID（外键）',
  `goods_name` VARCHAR(100) NOT NULL COMMENT '物品名称（非空）',
  `buy_year` YEAR COMMENT '购买年份（允许空）',
  `new_degree` VARCHAR(20) NOT NULL COMMENT '新旧程度（非空：全新/9成新/8成新/...）',
  `price` DECIMAL(10,2) NOT NULL COMMENT '转让价格（非空）',
  `location` VARCHAR(100) NOT NULL COMMENT '位置（非空）',
  `publish_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间（非空）',
  `status` ENUM('on_shelf','off_shelf') NOT NULL DEFAULT 'on_shelf' COMMENT '状态（非空）',
  CONSTRAINT `fk_goods_category41` FOREIGN KEY (`category_id`) REFERENCES `category41`(`category_id`),
  CONSTRAINT `fk_goods_publisher41` FOREIGN KEY (`publisher_id`) REFERENCES `user41`(`user_id`)
) COMMENT '二手物品表';

-- 4. 订单表（加后缀41）
CREATE TABLE `order41` (
  `order_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID（主键）',
  `user_id` INT NOT NULL COMMENT '用户ID（外键）',
  `goods_id` INT NOT NULL COMMENT '物品ID（外键）',
  `order_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '订单时间（非空）',
  `pay_status` ENUM('unpaid','paid') NOT NULL DEFAULT 'unpaid' COMMENT '支付状态（非空）',
  `amount` DECIMAL(10,2) NOT NULL COMMENT '订单金额（非空）',
  CONSTRAINT `fk_order_user41` FOREIGN KEY (`user_id`) REFERENCES `user41`(`user_id`),
  CONSTRAINT `fk_order_goods41` FOREIGN KEY (`goods_id`) REFERENCES `goods41`(`goods_id`)
) COMMENT '订单表';

-- 5. 收藏表（加后缀41）
CREATE TABLE `collection41` (
  `collection_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '收藏ID（主键）',
  `user_id` INT NOT NULL COMMENT '用户ID（外键）',
  `goods_id` INT NOT NULL COMMENT '物品ID（外键）',
  `collect_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间（非空）',
  CONSTRAINT `fk_collection_user41` FOREIGN KEY (`user_id`) REFERENCES `user41`(`user_id`),
  CONSTRAINT `fk_collection_goods41` FOREIGN KEY (`goods_id`) REFERENCES `goods41`(`goods_id`),
  CONSTRAINT `uk_user_goods_collect41` UNIQUE (`user_id`,`goods_id`)
) COMMENT '收藏表';

-- 6. 购物车表（加后缀41）
CREATE TABLE `cart41` (
  `cart_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '购物车ID（主键）',
  `user_id` INT NOT NULL COMMENT '用户ID（外键）',
  `goods_id` INT NOT NULL COMMENT '物品ID（外键）',
  `add_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '添加时间（非空）',
  CONSTRAINT `fk_cart_user41` FOREIGN KEY (`user_id`) REFERENCES `user41`(`user_id`),
  CONSTRAINT `fk_cart_goods41` FOREIGN KEY (`goods_id`) REFERENCES `goods41`(`goods_id`),
  CONSTRAINT `uk_user_goods_cart41` UNIQUE (`user_id`,`goods_id`)
) COMMENT '购物车表';

-- 7. 投诉表（加后缀41）
CREATE TABLE `complaint41` (
  `complaint_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '投诉ID（主键）',
  `order_id` INT NOT NULL COMMENT '订单ID（外键）',
  `complain_user_id` INT NOT NULL COMMENT '投诉用户ID（外键）',
  `complaint_type` VARCHAR(50) NOT NULL COMMENT '投诉类别（非空）',
  `complaint_reason` TEXT NOT NULL COMMENT '投诉原因（非空）',
  `complaint_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '投诉时间（非空）',
  `handle_status` ENUM('unhandled','handled') NOT NULL DEFAULT 'unhandled' COMMENT '处理状态（非空）',
  CONSTRAINT `fk_complaint_order41` FOREIGN KEY (`order_id`) REFERENCES `order41`(`order_id`),
  CONSTRAINT `fk_complaint_user41` FOREIGN KEY (`complain_user_id`) REFERENCES `user41`(`user_id`),
  CONSTRAINT `uk_order_complaint41` UNIQUE (`order_id`)
) COMMENT '投诉表';

-- 8. 投诉处理表（加后缀41）
CREATE TABLE `complaint_handle41` (
  `handle_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '处理ID（主键）',
  `complaint_id` INT NOT NULL COMMENT '投诉ID（外键）',
  `admin_id` INT NOT NULL COMMENT '管理员ID（外键）',
  `handle_opinion` TEXT NOT NULL COMMENT '处理意见（非空）',
  `handle_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '处理时间（非空）',
  CONSTRAINT `fk_handle_complaint41` FOREIGN KEY (`complaint_id`) REFERENCES `complaint41`(`complaint_id`),
  CONSTRAINT `fk_handle_admin41` FOREIGN KEY (`admin_id`) REFERENCES `user41`(`user_id`)
) COMMENT '投诉处理表';

-- 索引（非主键/外键）
CREATE INDEX idx_goods_name41 ON goods41(goods_name);

-- 视图
CREATE VIEW v_user_paid_orders41 AS
SELECT 
  o.order_id,
  u.username,
  g.goods_name,
  c.category_name,
  o.order_time,
  o.amount
FROM `order41` o
JOIN `user41` u ON o.user_id = u.user_id
JOIN `goods41` g ON o.goods_id = g.goods_id
JOIN `category41` c ON g.category_id = c.category_id
WHERE o.pay_status = 'paid';

-- 触发器
DELIMITER //
CREATE TRIGGER trg_update_complaint_status41
AFTER INSERT ON complaint_handle41
FOR EACH ROW
BEGIN
  UPDATE complaint41 
  SET handle_status = 'handled' 
  WHERE complaint_id = NEW.complaint_id;
END //
DELIMITER ;

-- 存储过程
DELIMITER //
CREATE PROCEDURE sp_freeze_user41(IN p_user_id INT)
BEGIN
  IF EXISTS (SELECT 1 FROM `user41` WHERE user_id = p_user_id) THEN
    UPDATE `user41` SET status = 'frozen' WHERE user_id = p_user_id;
    SELECT '用户账号已冻结' AS result;
  ELSE
    SELECT '用户不存在' AS result;
  END IF;
END //
DELIMITER ;