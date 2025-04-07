from django.test import TestCase
from shop_app.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

class UserProductTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='TestUser', 
                                             email='testemail@gmail.com', 
                                             password='130testpassword130')
        
        self.admin_user = User.objects.create_superuser(
            username = 'admin',
            email='admin@example.com',
            password='adminpassword'
        )

        self.client = APIClient()

        self.category = Category.objects.create(name='TestCategory')
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  
            content_type='image/jpeg'
        )


        self.product = Product.objects.create(
            user = self.user,
            category = self.category,
            image = self.image,
            name = 'test_product',
            description='Null',
            price = 100,
            tel_number = '+375291705757',
            city = 'minsk',
            discount = 0,
            stock = 1,
        )

        self.order = Order.objects.create(
            product = self.product,
            user = self.user,
            quantity_product = 1,
            address = 'TestStreet 26',
            tel_number = '+375291705757',
            payment = 'cash',
            price = self.product.price,
            comment = 'TestComment'
        )
        
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'test_product')
        self.assertEqual(self.product.user, self.user)
        self.assertEqual(self.product.category, self.category)
    
    def test_product_deletion(self):
        product_id = self.product.id
        self.product.delete()

        try:
            Product.objects.get(pk=product_id)
            self.fail("Product was not deleted")
        except Product.DoesNotExist:
            pass

    def test_update_product(self):
        self.product.discount = 10
        self.product.save()
        updated_product = Product.objects.get(pk=self.product.id)
        self.assertEqual(updated_product.discount, 10)

    def test_category_deletion_cascades_to_product(self):
        product_id = self.product.id
        self.category.delete()
        try:
            product = Product.objects.get(pk=product_id)
            self.fail("MB Category was deleted, but product - wasn't")
        except:
            pass
    
    def test_stock_product(self):
        self.product.stock = 10
        self.product.save()
        updated_pr = Product.objects.get(pk=self.product.id)
        self.assertGreaterEqual(updated_pr.stock, 1, "Stock shouldn't be <0")
    
    def test_get_api_products(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)

    def test_create_product_unauthenticated_api(self):
        url = reverse('products-list')
        
        data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': 99.99,
            'category': self.category.id 
        }
        post_response = self.client.post(url, data, format='json')
        self.assertEqual(post_response.status_code, 403)

    def test_create_category_not_admin(self):
        url = reverse('categories-list')

        data = {
            'name': 'TestCategory',
        }
        post_response = self.client.post(url, data, format='json')
        self.assertEqual(post_response.status_code, 403)

    def test_create_category_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('categories-list')
        data = {
            'name': 'TestAdminCategory'
        }

        post_response = self.client.post(url, data, format='json')
        self.assertEqual(post_response.status_code, 201)

    def test_delete_category_admin(self):
        self.client.force_authenticate(self.admin_user)
        url = reverse('categories-detail', kwargs={'pk': self.category.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        try:
            Category.objects.get(pk=self.category.id)
            self.fail(f"Category wasn't deleted")
        except:
            pass

    def test_delete_category_not_admin(self):
        url = reverse('categories-detail', kwargs={'pk': self.category.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        try:
            Category.objects.get(pk=self.category.id)
        except:
            self.fail("Category should not be deleted by non-admin")

    def test_make_order_authorized(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('orders-list')

        data = {
            'product': self.product.id,
            'quantity_product': 1,
            'address': 'New TestStreet 27',
            'tel_number': '+375291705757',
            'payment': 'cash',  
            'price': self.product.price,
            'comment': 'TestComment'
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, 201)

    def test_make_order_unauthorized(self):
        url = reverse('orders-list')
        data = {
            'product': self.product.id,
            'quantity_product': 1,
            'address': 'New TestStreet 27',
            'tel_number': '+375291705757',
            'payment': 'cash',  
            'price': self.product.price,
            'comment': 'TestComment'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_make_order_quantity_goods_more_than_exists(self):
        self.client.force_authenticate(self.admin_user)
        url = reverse('orders-list')
        data = {
            'product': self.product.id,
            'quantity_product': 5,
            'address': 'New TestStreet 27',
            'tel_number': '+375291705757',
            'payment': 'cash',  
            'price': self.product.price,
            'comment': 'TestComment'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
    