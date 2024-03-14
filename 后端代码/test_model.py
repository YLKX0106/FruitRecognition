import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf



def data_load(data_dir, test_data_dir, img_height, img_width, batch_size):

    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        label_mode='categorical',
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        test_data_dir,
        label_mode='categorical',
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)
    class_names = train_ds.class_names

    return train_ds, val_ds, class_names



def test_mobilenet():

    train_ds, test_ds, class_names = data_load("data/split_data/train",
                                               "data/split_data/test", 224, 224, 16)

    model = tf.keras.models.load_model("models/mobilenet_fv_0611.h5")

    loss, accuracy = model.evaluate(test_ds)

    print('Mobilenet test accuracy :', accuracy)

    test_real_labels = []
    test_pre_labels = []
    for test_batch_images, test_batch_labels in test_ds:
        test_batch_labels = test_batch_labels.numpy()
        test_batch_pres = model.predict(test_batch_images)


        test_batch_labels_max = np.argmax(test_batch_labels, axis=1)
        test_batch_pres_max = np.argmax(test_batch_pres, axis=1)



        for i in test_batch_labels_max:
            test_real_labels.append(i)

        for i in test_batch_pres_max:
            test_pre_labels.append(i)




    class_names_length = len(class_names)
    heat_maps = np.zeros((class_names_length, class_names_length))
    for test_real_label, test_pre_label in zip(test_real_labels, test_pre_labels):
        heat_maps[test_real_label][test_pre_label] = heat_maps[test_real_label][test_pre_label] + 1

    print(heat_maps)
    heat_maps_sum = np.sum(heat_maps, axis=1).reshape(-1, 1)

    print()
    heat_maps_float = heat_maps / heat_maps_sum
    print(heat_maps_float)

    show_heatmaps(title="heatmap", x_labels=class_names, y_labels=class_names, harvest=heat_maps_float,
                  save_name="results/heatmap_mobilenet.png")



def show_heatmaps(title, x_labels, y_labels, harvest, save_name):
    fig, ax = plt.subplots()
    im = ax.imshow(harvest, cmap="OrRd")
    ax.set_xticks(np.arange(len(y_labels)))
    ax.set_yticks(np.arange(len(x_labels)))
    ax.set_xticklabels(y_labels)
    ax.set_yticklabels(x_labels)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    for i in range(len(x_labels)):
        for j in range(len(y_labels)):
            text = ax.text(j, i, round(harvest[i, j], 2),
                           ha="center", va="center", color="black")
    ax.set_xlabel("Predict label")
    ax.set_ylabel("Actual label")
    ax.set_title(title)
    fig.tight_layout()
    plt.colorbar(im)
    plt.savefig(save_name, dpi=100)



if __name__ == '__main__':

    test_mobilenet()
