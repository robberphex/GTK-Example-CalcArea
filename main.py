from gi.repository import Gtk, Gdk, GdkPixbuf
from PIL import Image, ImageDraw
from io import BytesIO
from math import pi

class Model:
    '''
    模型类
    存储半径，计算周长、面积、体积
    '''

    def __init__(self):
        self._radius = 0

    def setRadius(self, radius):
        self._radius = float(radius)

    def getRadius(self):
        return self._radius

    def getPerimeter(self):
        return pi * self._radius * 2

    def getArea(self):
        return self._radius ** 2 * pi

    def getVolume(self):
        return 4 * pi * self._radius ** 3 / 3


class Controller:
    '''
    控制器类
    控制视图和模型的更新
    '''

    def __init__(self, model):
        self.model = model
        self._observers = []

    def addObserver(self, observer):
        self._observers.append(observer)

    def setRadius(self, radius):
        model.setRadius(radius)
        self.notify()

    def notify(self):
        for observer in self._observers:
            observer.update()


class TextView:
    '''
    文字视图类
    处理文本输入框的视图
    '''

    def __init__(self, model, rEntry, pEntry, aEntry, vEntry):
        '''
        :type model Model
        '''
        self.model = model
        self.rEntry = rEntry
        self.pEntry = pEntry
        self.aEntry = aEntry
        self.vEntry = vEntry

    def update(self):
        self.rEntry.set_text('%2.2f' % self.model.getRadius())
        self.pEntry.set_text('%2.2f' % self.model.getPerimeter())
        self.aEntry.set_text('%2.2f' % self.model.getArea())
        self.vEntry.set_text('%2.2f' % self.model.getVolume())


class ScaleView:
    '''
    拖动条视图
    处理拖动条的视图
    '''

    def __init__(self, model, scale):
        '''
        :type model Model
        '''
        self.model = model
        self.scale = scale

    def update(self):
        self.scale.set_value(self.model.getRadius())


class ImageView:
    '''
    图像视图
    处理图像的视图
    '''

    @classmethod
    def imgToPixbuf(cls, img):
        '''
        :type img Image
        '''
        buff = BytesIO()
        img.save(buff, 'ppm')
        contents = buff.getvalue()
        buff.close()

        loader = GdkPixbuf.PixbufLoader.new_with_type('pnm')
        loader.write(contents)
        pixbuf = loader.get_pixbuf()
        loader.close()
        return pixbuf

    @classmethod
    def ellipse(cls, radius):
        '''
        :type radius int
        '''
        image = Image.new("RGBA", (300, 300), "white")
        draw = ImageDraw.Draw(image)
        minor = 150 - radius
        major = 150 + radius
        draw.ellipse((minor, minor, major, major), outline='red')
        pixbuf = ImageView.imgToPixbuf(image)
        return pixbuf

    def __init__(self, model, image):
        self.model = model
        self.image = image

    def update(self):
        radius = self.model.getRadius()
        pixbuf = ImageView.ellipse(radius)
        self.image.set_from_pixbuf(pixbuf)


class MainWindow(Gtk.Window):
    '''
    主窗口类
    负责整体界面的显示
    '''

    def textCallback(self, widget, controller):
        '''
        文本输入回调
        '''
        try:
            radius = float(widget.get_text())
            controller.setRadius(radius)
        except ValueError as e:
            pass

    def scaleCallback(self, widget, controller):
        '''
        拖动条回调
        '''
        radius = widget.get_value()
        controller.setRadius(radius)

    def __init__(self):
        Gtk.Window.__init__(self, title="Title")

        self.set_default_size(600, 400)
        self.set_position(Gtk.WindowPosition.CENTER)

        hbox = Gtk.HBox(spacing=5)
        self.add(hbox)

        vbox = Gtk.VBox(spacing=5)
        hbox.pack_start(vbox, True, True, 2)

        table = Gtk.Table.new(4, 2, False)
        vbox.pack_start(table, True, True, 2)

        label = Gtk.Label('半径：')
        table.attach_defaults(label, 0, 1, 0, 1)
        label = Gtk.Label('周长：')
        table.attach_defaults(label, 0, 1, 1, 2)
        label = Gtk.Label('面积：')
        table.attach_defaults(label, 0, 1, 2, 3)
        label = Gtk.Label('体积：')
        table.attach_defaults(label, 0, 1, 3, 4)

        self.radiusEntry = Gtk.Entry.new()
        self.radiusEntry.connect('changed', self.textCallback, controller)
        table.attach_defaults(self.radiusEntry, 1, 2, 0, 1)
        self.perimeterEntry = Gtk.Entry.new()
        self.perimeterEntry.set_sensitive(False)
        self.perimeterEntry.set_text('周长')
        table.attach_defaults(self.perimeterEntry, 1, 2, 1, 2)
        self.areaEntry = Gtk.Entry.new()
        self.areaEntry.set_sensitive(False)
        self.areaEntry.set_text('面积')
        table.attach_defaults(self.areaEntry, 1, 2, 2, 3)
        self.volumeEntry = Gtk.Entry.new()
        self.volumeEntry.set_sensitive(False)
        self.volumeEntry.set_text('体积')
        table.attach_defaults(self.volumeEntry, 1, 2, 3, 4)

        self.scale = Gtk.HScale.new_with_range(0, 100, 1)
        self.scale.connect('value-changed', self.scaleCallback, controller)
        vbox.pack_start(self.scale, False, False, 2)

        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 300, 300)
        pixbuf.fill(0xaaaaaaaa)
        self.image = Gtk.Image.new_from_pixbuf(pixbuf)
        hbox.pack_start(self.image, True, True, 2)

        self.connect('delete-event', Gtk.main_quit)


model = Model()
controller = Controller(model)

if __name__ == '__main__':
    Gdk.threads_init()
    Gdk.threads_enter()
    win = MainWindow()

    iv = ImageView(model, win.image)
    controller.addObserver(iv)

    tv = TextView(model, win.radiusEntry, win.perimeterEntry, win.areaEntry, win.volumeEntry)
    controller.addObserver(tv)

    sv = ScaleView(model, win.scale)
    controller.addObserver(sv)

    win.show_all()
    Gtk.main()
    Gdk.threads_leave()
